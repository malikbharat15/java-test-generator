package com.bank.core.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import java.math.BigDecimal;
import java.util.List;
import java.util.ArrayList;

/**
 * Account Management REST API
 * Handles CRUD operations for bank accounts
 */
@RestController
@RequestMapping("/api/v1/accounts")
public class AccountController {

    @GetMapping
    public ResponseEntity<List<Account>> getAllAccounts(
            @RequestParam(required = false) String customerId,
            @RequestParam(required = false) String accountType,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        List<Account> accounts = new ArrayList<>();
        return ResponseEntity.ok(accounts);
    }

    @GetMapping("/{accountNumber}")
    public ResponseEntity<Account> getAccountByNumber(@PathVariable String accountNumber) {
        Account account = new Account(accountNumber, "John Doe", "SAVINGS", new BigDecimal("10000.00"));
        return ResponseEntity.ok(account);
    }

    @PostMapping
    public ResponseEntity<Account> createAccount(@RequestBody AccountRequest request) {
        Account account = new Account(
            generateAccountNumber(),
            request.getCustomerName(),
            request.getAccountType(),
            BigDecimal.ZERO
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(account);
    }

    @PutMapping("/{accountNumber}")
    public ResponseEntity<Account> updateAccount(
            @PathVariable String accountNumber,
            @RequestBody AccountRequest request) {
        Account account = new Account(accountNumber, request.getCustomerName(), 
                                      request.getAccountType(), new BigDecimal("5000.00"));
        return ResponseEntity.ok(account);
    }

    @DeleteMapping("/{accountNumber}")
    public ResponseEntity<Void> closeAccount(@PathVariable String accountNumber) {
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/{accountNumber}/balance")
    public ResponseEntity<BalanceResponse> getAccountBalance(@PathVariable String accountNumber) {
        BalanceResponse response = new BalanceResponse(accountNumber, new BigDecimal("10000.00"), "USD");
        return ResponseEntity.ok(response);
    }

    @PatchMapping("/{accountNumber}/status")
    public ResponseEntity<Account> updateAccountStatus(
            @PathVariable String accountNumber,
            @RequestParam String status) {
        return ResponseEntity.ok(null);
    }

    private String generateAccountNumber() {
        return "ACC" + System.currentTimeMillis();
    }

    // Inner classes
    static class Account {
        private String accountNumber;
        private String customerName;
        private String accountType;
        private BigDecimal balance;

        public Account(String accountNumber, String customerName, String accountType, BigDecimal balance) {
            this.accountNumber = accountNumber;
            this.customerName = customerName;
            this.accountType = accountType;
            this.balance = balance;
        }

        // Getters and setters omitted for brevity
    }

    static class AccountRequest {
        private String customerName;
        private String accountType;

        public String getCustomerName() { return customerName; }
        public String getAccountType() { return accountType; }
    }

    static class BalanceResponse {
        private String accountNumber;
        private BigDecimal balance;
        private String currency;

        public BalanceResponse(String accountNumber, BigDecimal balance, String currency) {
            this.accountNumber = accountNumber;
            this.balance = balance;
            this.currency = currency;
        }
    }
}
