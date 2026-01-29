package com.inventory.reactive.model;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.PositiveOrZero;

/**
 * Stock update request DTO
 */
public class StockUpdate {
    
    @NotBlank
    private String productId;
    
    @NotNull
    @PositiveOrZero
    private Integer newQuantity;
    
    private String reason;

    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }
    
    public Integer getNewQuantity() { return newQuantity; }
    public void setNewQuantity(Integer newQuantity) { this.newQuantity = newQuantity; }
    
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
}
