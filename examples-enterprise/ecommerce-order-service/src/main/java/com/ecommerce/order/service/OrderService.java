package com.ecommerce.order.service;

import com.ecommerce.order.model.Order;
import com.ecommerce.order.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    private static final String ORDER_CREATED_TOPIC = "order-created";
    private static final String ORDER_STATUS_CHANGED_TOPIC = "order-status-changed";

    @Transactional
    public Order createOrder(Order order) {
        Order savedOrder = orderRepository.save(order);
        
        // Publish Kafka event
        kafkaTemplate.send(ORDER_CREATED_TOPIC, 
            String.format("Order %d created for customer %s", 
                savedOrder.getId(), savedOrder.getCustomerName()));
        
        return savedOrder;
    }

    public Optional<Order> getOrder(Long id) {
        return orderRepository.findById(id);
    }

    public List<Order> getAllOrders() {
        return orderRepository.findAll();
    }

    public List<Order> getOrdersByCustomer(String customerName) {
        return orderRepository.findByCustomerName(customerName);
    }

    public List<Order> getOrdersByStatus(Order.OrderStatus status) {
        return orderRepository.findByStatus(status);
    }

    @Transactional
    public Order updateOrderStatus(Long id, Order.OrderStatus newStatus) {
        Optional<Order> orderOpt = orderRepository.findById(id);
        
        if (orderOpt.isPresent()) {
            Order order = orderOpt.get();
            Order.OrderStatus oldStatus = order.getStatus();
            order.setStatus(newStatus);
            Order updatedOrder = orderRepository.save(order);
            
            // Publish status change event
            kafkaTemplate.send(ORDER_STATUS_CHANGED_TOPIC,
                String.format("Order %d status changed from %s to %s",
                    id, oldStatus, newStatus));
            
            return updatedOrder;
        }
        
        throw new RuntimeException("Order not found: " + id);
    }

    @Transactional
    public void cancelOrder(Long id) {
        updateOrderStatus(id, Order.OrderStatus.CANCELLED);
    }

    public List<Order> findStaleOrders(int hoursAgo) {
        LocalDateTime cutoff = LocalDateTime.now().minusHours(hoursAgo);
        return orderRepository.findStaleOrders(cutoff);
    }

    public long countOrdersByStatus(Order.OrderStatus status) {
        return orderRepository.countByStatus(status);
    }
}
