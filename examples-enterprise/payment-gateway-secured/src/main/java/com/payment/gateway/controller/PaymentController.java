package com.payment.gateway.controller;

import com.payment.gateway.dto.*;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * Payment Processing REST API
 * All endpoints require authentication, some require specific roles
 */
@RestController
@RequestMapping("/api/v1/payments")
@Validated
public class PaymentController {

    /**
     * Process a new payment - requires USER or MERCHANT role
     */
    @PostMapping
    @PreAuthorize("hasAnyRole('USER', 'MERCHANT')")
    public ResponseEntity<PaymentResponse> processPayment(
            @Valid @RequestBody PaymentRequest request) {
        PaymentResponse response = new PaymentResponse();
        response.setTransactionId("TXN" + System.currentTimeMillis());
        response.setStatus("PENDING");
        return ResponseEntity.ok(response);
    }

    /**
     * Get payment by transaction ID - authenticated users only
     */
    @GetMapping("/{transactionId}")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<PaymentResponse> getPayment(
            @PathVariable String transactionId) {
        return ResponseEntity.ok(new PaymentResponse());
    }

    /**
     * Get all payments for current user
     */
    @GetMapping("/my-payments")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<List<PaymentResponse>> getMyPayments(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String status) {
        return ResponseEntity.ok(List.of());
    }

    /**
     * Refund a payment - MERCHANT or ADMIN only
     */
    @PostMapping("/{transactionId}/refund")
    @PreAuthorize("hasAnyRole('MERCHANT', 'ADMIN')")
    public ResponseEntity<RefundResponse> refundPayment(
            @PathVariable String transactionId,
            @Valid @RequestBody RefundRequest request) {
        return ResponseEntity.ok(new RefundResponse());
    }

    /**
     * Cancel a pending payment
     */
    @DeleteMapping("/{transactionId}")
    @PreAuthorize("hasAnyRole('USER', 'MERCHANT', 'ADMIN')")
    public ResponseEntity<Void> cancelPayment(
            @PathVariable String transactionId,
            @RequestParam(required = false) String reason) {
        return ResponseEntity.noContent().build();
    }

    /**
     * Get payment statistics - ADMIN only
     */
    @GetMapping("/admin/statistics")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<PaymentStatistics> getStatistics(
            @RequestParam String startDate,
            @RequestParam String endDate,
            @RequestParam(required = false) String merchantId) {
        return ResponseEntity.ok(new PaymentStatistics());
    }

    /**
     * Get all merchant payments - ADMIN only
     */
    @GetMapping("/admin/merchant/{merchantId}/payments")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<PaymentResponse>> getMerchantPayments(
            @PathVariable String merchantId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size) {
        return ResponseEntity.ok(List.of());
    }

    // DTO classes
    public static class PaymentRequest {
        @javax.validation.constraints.NotNull
        @javax.validation.constraints.Size(min = 16, max = 19)
        private String cardNumber;

        @javax.validation.constraints.NotBlank
        private String cardHolderName;

        @javax.validation.constraints.Pattern(regexp = "\\d{2}/\\d{2}")
        private String expiryDate;

        @javax.validation.constraints.Size(min = 3, max = 4)
        private String cvv;

        @javax.validation.constraints.Positive
        @javax.validation.constraints.DecimalMin("0.01")
        private java.math.BigDecimal amount;

        @javax.validation.constraints.NotBlank
        @javax.validation.constraints.Size(min = 3, max = 3)
        private String currency;

        private String merchantId;
        private String orderId;
        private String description;

        // Getters and setters
        public String getCardNumber() { return cardNumber; }
        public void setCardNumber(String cardNumber) { this.cardNumber = cardNumber; }
        public String getCardHolderName() { return cardHolderName; }
        public void setCardHolderName(String cardHolderName) { this.cardHolderName = cardHolderName; }
        public String getExpiryDate() { return expiryDate; }
        public void setExpiryDate(String expiryDate) { this.expiryDate = expiryDate; }
        public String getCvv() { return cvv; }
        public void setCvv(String cvv) { this.cvv = cvv; }
        public java.math.BigDecimal getAmount() { return amount; }
        public void setAmount(java.math.BigDecimal amount) { this.amount = amount; }
        public String getCurrency() { return currency; }
        public void setCurrency(String currency) { this.currency = currency; }
        public String getMerchantId() { return merchantId; }
        public void setMerchantId(String merchantId) { this.merchantId = merchantId; }
        public String getOrderId() { return orderId; }
        public void setOrderId(String orderId) { this.orderId = orderId; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
    }

    public static class PaymentResponse {
        private String transactionId;
        private String status;
        private java.math.BigDecimal amount;
        private String currency;
        private java.time.LocalDateTime processedAt;
        private String authorizationCode;

        // Getters and setters
        public String getTransactionId() { return transactionId; }
        public void setTransactionId(String transactionId) { this.transactionId = transactionId; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public java.math.BigDecimal getAmount() { return amount; }
        public void setAmount(java.math.BigDecimal amount) { this.amount = amount; }
        public String getCurrency() { return currency; }
        public void setCurrency(String currency) { this.currency = currency; }
        public java.time.LocalDateTime getProcessedAt() { return processedAt; }
        public void setProcessedAt(java.time.LocalDateTime processedAt) { this.processedAt = processedAt; }
        public String getAuthorizationCode() { return authorizationCode; }
        public void setAuthorizationCode(String authorizationCode) { this.authorizationCode = authorizationCode; }
    }

    public static class RefundRequest {
        @javax.validation.constraints.Positive
        private java.math.BigDecimal amount;
        
        @javax.validation.constraints.NotBlank
        @javax.validation.constraints.Size(max = 500)
        private String reason;

        public java.math.BigDecimal getAmount() { return amount; }
        public void setAmount(java.math.BigDecimal amount) { this.amount = amount; }
        public String getReason() { return reason; }
        public void setReason(String reason) { this.reason = reason; }
    }

    public static class RefundResponse {
        private String refundId;
        private String originalTransactionId;
        private java.math.BigDecimal refundAmount;
        private String status;

        public String getRefundId() { return refundId; }
        public void setRefundId(String refundId) { this.refundId = refundId; }
        public String getOriginalTransactionId() { return originalTransactionId; }
        public void setOriginalTransactionId(String originalTransactionId) { this.originalTransactionId = originalTransactionId; }
        public java.math.BigDecimal getRefundAmount() { return refundAmount; }
        public void setRefundAmount(java.math.BigDecimal refundAmount) { this.refundAmount = refundAmount; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
    }

    public static class PaymentStatistics {
        private long totalTransactions;
        private java.math.BigDecimal totalVolume;
        private java.math.BigDecimal averageTransactionValue;
        private double successRate;
        
        public long getTotalTransactions() { return totalTransactions; }
        public void setTotalTransactions(long totalTransactions) { this.totalTransactions = totalTransactions; }
        public java.math.BigDecimal getTotalVolume() { return totalVolume; }
        public void setTotalVolume(java.math.BigDecimal totalVolume) { this.totalVolume = totalVolume; }
        public java.math.BigDecimal getAverageTransactionValue() { return averageTransactionValue; }
        public void setAverageTransactionValue(java.math.BigDecimal averageTransactionValue) { this.averageTransactionValue = averageTransactionValue; }
        public double getSuccessRate() { return successRate; }
        public void setSuccessRate(double successRate) { this.successRate = successRate; }
    }
}
