package com.payment.gateway.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * Webhook Management Controller
 * Configure payment event webhooks
 */
@RestController
@RequestMapping("/api/v1/webhooks")
public class WebhookController {

    /**
     * Register a new webhook - MERCHANT only
     */
    @PostMapping
    @PreAuthorize("hasRole('MERCHANT')")
    public ResponseEntity<WebhookResponse> createWebhook(
            @Valid @RequestBody WebhookRequest request) {
        return ResponseEntity.ok(new WebhookResponse());
    }

    /**
     * List all webhooks for merchant
     */
    @GetMapping
    @PreAuthorize("hasRole('MERCHANT')")
    public ResponseEntity<List<WebhookResponse>> listWebhooks() {
        return ResponseEntity.ok(List.of());
    }

    /**
     * Update webhook configuration
     */
    @PutMapping("/{webhookId}")
    @PreAuthorize("hasRole('MERCHANT')")
    public ResponseEntity<WebhookResponse> updateWebhook(
            @PathVariable String webhookId,
            @Valid @RequestBody WebhookRequest request) {
        return ResponseEntity.ok(new WebhookResponse());
    }

    /**
     * Delete a webhook
     */
    @DeleteMapping("/{webhookId}")
    @PreAuthorize("hasRole('MERCHANT')")
    public ResponseEntity<Void> deleteWebhook(@PathVariable String webhookId) {
        return ResponseEntity.noContent().build();
    }

    /**
     * Test webhook delivery
     */
    @PostMapping("/{webhookId}/test")
    @PreAuthorize("hasRole('MERCHANT')")
    public ResponseEntity<WebhookTestResult> testWebhook(@PathVariable String webhookId) {
        return ResponseEntity.ok(new WebhookTestResult());
    }

    // DTOs
    public static class WebhookRequest {
        @javax.validation.constraints.NotBlank
        @org.hibernate.validator.constraints.URL
        private String url;
        
        @javax.validation.constraints.NotEmpty
        private List<String> events; // PAYMENT_SUCCESS, PAYMENT_FAILED, REFUND_COMPLETED
        
        private String secret;
        private boolean active = true;

        public String getUrl() { return url; }
        public void setUrl(String url) { this.url = url; }
        public List<String> getEvents() { return events; }
        public void setEvents(List<String> events) { this.events = events; }
        public String getSecret() { return secret; }
        public void setSecret(String secret) { this.secret = secret; }
        public boolean isActive() { return active; }
        public void setActive(boolean active) { this.active = active; }
    }

    public static class WebhookResponse {
        private String webhookId;
        private String url;
        private List<String> events;
        private boolean active;
        private java.time.LocalDateTime createdAt;

        public String getWebhookId() { return webhookId; }
        public void setWebhookId(String webhookId) { this.webhookId = webhookId; }
        public String getUrl() { return url; }
        public void setUrl(String url) { this.url = url; }
        public List<String> getEvents() { return events; }
        public void setEvents(List<String> events) { this.events = events; }
        public boolean isActive() { return active; }
        public void setActive(boolean active) { this.active = active; }
        public java.time.LocalDateTime getCreatedAt() { return createdAt; }
        public void setCreatedAt(java.time.LocalDateTime createdAt) { this.createdAt = createdAt; }
    }

    public static class WebhookTestResult {
        private boolean success;
        private int statusCode;
        private String responseBody;
        private long responseTimeMs;

        public boolean isSuccess() { return success; }
        public void setSuccess(boolean success) { this.success = success; }
        public int getStatusCode() { return statusCode; }
        public void setStatusCode(int statusCode) { this.statusCode = statusCode; }
        public String getResponseBody() { return responseBody; }
        public void setResponseBody(String responseBody) { this.responseBody = responseBody; }
        public long getResponseTimeMs() { return responseTimeMs; }
        public void setResponseTimeMs(long responseTimeMs) { this.responseTimeMs = responseTimeMs; }
    }
}
