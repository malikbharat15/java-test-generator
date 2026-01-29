"""
Debug script to understand Kafka annotation structure
"""
import javalang

code = '''
package com.bank.fraud.listener;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class FraudDetectionListener {

    @KafkaListener(topics = "transaction-events", groupId = "fraud-detection")
    public void analyzeTransaction(String transactionEvent) {
        System.out.println("Test");
    }
}
'''

tree = javalang.parse.parse(code)

for path, node in tree.filter(javalang.tree.ClassDeclaration):
    print(f"Class: {node.name}")
    for method in node.methods:
        print(f"\n  Method: {method.name}")
        if method.annotations:
            for ann in method.annotations:
                print(f"    Annotation: {ann.name}")
                print(f"    Element type: {type(ann.element)}")
                print(f"    Element: {ann.element}")
                
                if ann.element:
                    print(f"    Has 'values': {hasattr(ann.element, 'values')}")
                    print(f"    Has 'value': {hasattr(ann.element, 'value')}")
                    
                    if hasattr(ann.element, 'values'):
                        print(f"    Values: {ann.element.values}")
                        for val in ann.element.values:
                            print(f"      - Type: {type(val)}")
                            print(f"      - Name: {getattr(val, 'name', 'NO NAME')}")
                            print(f"      - Value: {getattr(val, 'value', 'NO VALUE')}")
                            
                            if hasattr(val, 'value'):
                                print(f"        Value type: {type(val.value)}")
                                if isinstance(val.value, javalang.tree.Literal):
                                    print(f"        Literal value: {val.value.value}")
