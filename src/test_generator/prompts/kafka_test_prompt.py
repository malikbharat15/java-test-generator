"""
Kafka Consumer Smoke Test Prompt
"""

KAFKA_TEST_PROMPT = """
SPECIALIZATION: Kafka Consumer Smoke Tests
==========================================

TEST APPROACH:
- Verify Kafka consumer is running and connected
- Send test message to topic
- Verify consumer processes message (check logs or side effects)
- Use @EmbeddedKafka for isolated tests OR connect to DEV Kafka

JUNIT 5 + EMBEDDED KAFKA:
```java
@SpringBootTest
@EmbeddedKafka(topics = {"orderCreated", "orderUpdated"})
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class OrderEventConsumerSmokeTest {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Test
    @Timeout(10)
    void shouldConsumeOrderCreatedEvent() throws Exception {
        String testMessage = "{\\"orderId\\": \\"smoke-test-123\\"}";
        
        kafkaTemplate.send("orderCreated", testMessage).get();
        
        // Wait for consumer to process
        await().atMost(5, SECONDS)
            .until(() -> consumerProcessedMessage());
    }
}
```

DETECTION:
- @KafkaListener annotation
- spring-kafka dependency
"""

def get_kafka_test_prompt():
    return KAFKA_TEST_PROMPT
