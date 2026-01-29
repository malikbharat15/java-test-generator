package com.ecommerce.order.kafka;

import com.ecommerce.order.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class PaymentEventListener {

    @Autowired
    private OrderService orderService;

    @KafkaListener(topics = "payment-completed", groupId = "order-service-group")
    public void handlePaymentCompleted(String message) {
        System.out.println("Payment completed event received: " + message);
        
        // Parse message and update order status
        // Format: "ORDER_ID:123|STATUS:PAID"
        if (message.contains("ORDER_ID:")) {
            String[] parts = message.split("\\|");
            String orderIdStr = parts[0].split(":")[1];
            Long orderId = Long.parseLong(orderIdStr);
            
            orderService.updateOrderStatus(orderId, com.ecommerce.order.model.Order.OrderStatus.CONFIRMED);
        }
    }

    @KafkaListener(topics = "payment-failed", groupId = "order-service-group")
    public void handlePaymentFailed(String message) {
        System.out.println("Payment failed event received: " + message);
        
        if (message.contains("ORDER_ID:")) {
            String orderIdStr = message.split("ORDER_ID:")[1].split("\\|")[0];
            Long orderId = Long.parseLong(orderIdStr);
            
            orderService.cancelOrder(orderId);
        }
    }

    @KafkaListener(topics = "shipment-dispatched", groupId = "order-service-group")
    public void handleShipmentDispatched(String message) {
        System.out.println("Shipment dispatched event received: " + message);
        
        if (message.contains("ORDER_ID:")) {
            String orderIdStr = message.split("ORDER_ID:")[1].split("\\|")[0];
            Long orderId = Long.parseLong(orderIdStr);
            
            orderService.updateOrderStatus(orderId, com.ecommerce.order.model.Order.OrderStatus.SHIPPED);
        }
    }
}
