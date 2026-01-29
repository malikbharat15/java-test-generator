package com.bank.core.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Transaction Management REST API
 * Handles transfers, deposits, and withdrawals
 */
@RestController
@RequestMapping("/api/v1/transactions")
public class TransactionController {

    @PostMapping("/transfer")
    public ResponseEntity<TransactionResponse> transferFunds(@RequestBody TransferRequest request) {
        TransactionResponse response = new TransactionResponse(
            "TXN" + System.currentTimeMillis(),
            "COMPLETED",
            LocalDateTime.now()
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @PostMapping("/deposit")
    public ResponseEntity<TransactionResponse> deposit(@RequestBody DepositRequest request) {
        TransactionResponse response = new TransactionResponse(
            "TXN" + System.currentTimeMillis(),
            "COMPLETED",
            LocalDateTime.now()
        );
        return ResponseEntity.ok(response);
    }

    @PostMapping("/withdraw")
    public ResponseEntity<TransactionResponse> withdraw(@RequestBody WithdrawRequest request) {
        TransactionResponse response = new TransactionResponse(
            "TXN" + System.currentTimeMillis(),
            "COMPLETED",
            LocalDateTime.now()
        );
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{transactionId}")
    public ResponseEntity<TransactionDetails> getTransactionDetails(@PathVariable String transactionId) {
        TransactionDetails details = new TransactionDetails(
            transactionId,
            "TRANSFER",
            new BigDecimal("500.00"),
            "COMPLETED"
        );
        return ResponseEntity.ok(details);
    }

    @GetMapping("/account/{accountNumber}")
    public ResponseEntity<Object> getAccountTransactions(
            @PathVariable String accountNumber,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size) {
        return ResponseEntity.ok(null);
    }

    @GetMapping("/{transactionId}/status")
    public ResponseEntity<TransactionStatus> getTransactionStatus(@PathVariable String transactionId) {
        TransactionStatus status = new TransactionStatus(transactionId, "COMPLETED", null);
        return ResponseEntity.ok(status);
    }

    // Inner classes
    static class TransferRequest {
        private String fromAccount;
        private String toAccount;
        private BigDecimal amount;
        private String currency;
        private String description;
    }

    static class DepositRequest {
        private String accountNumber;
        private BigDecimal amount;
        private String currency;
    }

    static class WithdrawRequest {
        private String accountNumber;
        private BigDecimal amount;
        private String currency;
    }

    static class TransactionResponse {
        private String transactionId;
        private String status;
        private LocalDateTime timestamp;

        public TransactionResponse(String transactionId, String status, LocalDateTime timestamp) {
            this.transactionId = transactionId;
            this.status = status;
            this.timestamp = timestamp;
        }
    }

    static class TransactionDetails {
        private String transactionId;
        private String type;
        private BigDecimal amount;
        private String status;

        public TransactionDetails(String transactionId, String type, BigDecimal amount, String status) {
            this.transactionId = transactionId;
            this.type = type;
            this.amount = amount;
            this.status = status;
        }
    }

    static class TransactionStatus {
        private String transactionId;
        private String status;
        private String errorMessage;

        public TransactionStatus(String transactionId, String status, String errorMessage) {
            this.transactionId = transactionId;
            this.status = status;
            this.errorMessage = errorMessage;
        }
    }
}
