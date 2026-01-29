package com.data.pipeline.processor;

import com.data.pipeline.model.Customer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

/**
 * Processor for customer data validation and transformation
 */
@Component
public class CustomerProcessor implements ItemProcessor<Customer, Customer> {

    private static final Logger logger = LoggerFactory.getLogger(CustomerProcessor.class);

    @Override
    public Customer process(Customer customer) throws Exception {
        logger.debug("Processing customer: {}", customer.getId());
        
        // Normalize email to lowercase
        if (customer.getEmail() != null) {
            customer.setEmail(customer.getEmail().toLowerCase().trim());
        }
        
        // Normalize names
        customer.setFirstName(capitalizeFirst(customer.getFirstName()));
        customer.setLastName(capitalizeFirst(customer.getLastName()));
        
        // Set default tier if not present
        if (customer.getTier() == null || customer.getTier().isEmpty()) {
            customer.setTier("STANDARD");
        }
        
        // Validate phone format
        if (customer.getPhone() != null) {
            customer.setPhone(customer.getPhone().replaceAll("[^0-9+]", ""));
        }
        
        return customer;
    }

    private String capitalizeFirst(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1).toLowerCase();
    }
}
