package com.bank.core.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

/**
 * Customer Management REST API
 * Handles customer profile operations
 */
@RestController
@RequestMapping("/api/v1/customers")
public class CustomerController {

    @GetMapping
    public ResponseEntity<Object> getAllCustomers(
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(null);
    }

    @GetMapping("/{customerId}")
    public ResponseEntity<Customer> getCustomerById(@PathVariable String customerId) {
        Customer customer = new Customer(customerId, "John Doe", "john.doe@bank.com", "1234567890");
        return ResponseEntity.ok(customer);
    }

    @PostMapping
    public ResponseEntity<Customer> createCustomer(@RequestBody CustomerRequest request) {
        Customer customer = new Customer(
            "CUST" + System.currentTimeMillis(),
            request.getName(),
            request.getEmail(),
            request.getPhone()
        );
        return ResponseEntity.ok(customer);
    }

    @PutMapping("/{customerId}")
    public ResponseEntity<Customer> updateCustomer(
            @PathVariable String customerId,
            @RequestBody CustomerRequest request) {
        return ResponseEntity.ok(null);
    }

    @DeleteMapping("/{customerId}")
    public ResponseEntity<Void> deleteCustomer(@PathVariable String customerId) {
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/{customerId}/accounts")
    public ResponseEntity<Object> getCustomerAccounts(@PathVariable String customerId) {
        return ResponseEntity.ok(null);
    }

    // Inner classes
    static class Customer {
        private String customerId;
        private String name;
        private String email;
        private String phone;

        public Customer(String customerId, String name, String email, String phone) {
            this.customerId = customerId;
            this.name = name;
            this.email = email;
            this.phone = phone;
        }
    }

    static class CustomerRequest {
        private String name;
        private String email;
        private String phone;

        public String getName() { return name; }
        public String getEmail() { return email; }
        public String getPhone() { return phone; }
    }
}
