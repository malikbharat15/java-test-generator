package com.ecommerce.order.scheduled;

import com.ecommerce.order.model.Order;
import com.ecommerce.order.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class OrderMaintenanceScheduler {

    @Autowired
    private OrderService orderService;

    /**
     * Check for stale pending orders every 30 minutes
     */
    @Scheduled(fixedRate = 1800000) // 30 minutes
    public void checkStalePendingOrders() {
        System.out.println("Checking for stale pending orders...");
        
        List<Order> staleOrders = orderService.findStaleOrders(24);
        
        for (Order order : staleOrders) {
            System.out.println("Found stale order: " + order.getId());
            // Could auto-cancel or alert
        }
    }

    /**
     * Generate daily order metrics at 1 AM
     */
    @Scheduled(cron = "0 0 1 * * *")
    public void generateDailyMetrics() {
        System.out.println("Generating daily order metrics...");
        
        long pendingCount = orderService.countOrdersByStatus(Order.OrderStatus.PENDING);
        long confirmedCount = orderService.countOrdersByStatus(Order.OrderStatus.CONFIRMED);
        long processingCount = orderService.countOrdersByStatus(Order.OrderStatus.PROCESSING);
        long shippedCount = orderService.countOrdersByStatus(Order.OrderStatus.SHIPPED);
        long deliveredCount = orderService.countOrdersByStatus(Order.OrderStatus.DELIVERED);
        long cancelledCount = orderService.countOrdersByStatus(Order.OrderStatus.CANCELLED);
        
        System.out.println(String.format(
            "Daily Metrics - Pending: %d, Confirmed: %d, Processing: %d, Shipped: %d, Delivered: %d, Cancelled: %d",
            pendingCount, confirmedCount, processingCount, shippedCount, deliveredCount, cancelledCount));
    }

    /**
     * Sync order status with warehouse every 15 minutes
     */
    @Scheduled(fixedRate = 900000) // 15 minutes
    public void syncWithWarehouse() {
        System.out.println("Syncing order status with warehouse...");
        
        List<Order> processingOrders = orderService.getOrdersByStatus(Order.OrderStatus.PROCESSING);
        
        for (Order order : processingOrders) {
            // Simulate warehouse status check
            System.out.println("Checking warehouse status for order: " + order.getId());
        }
    }
}
