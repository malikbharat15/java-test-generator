package com.inventory.reactive;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Reactive Inventory Service
 * Uses Spring WebFlux for non-blocking operations
 */
@SpringBootApplication
public class InventoryReactiveApplication {
    public static void main(String[] args) {
        SpringApplication.run(InventoryReactiveApplication.class, args);
    }
}
