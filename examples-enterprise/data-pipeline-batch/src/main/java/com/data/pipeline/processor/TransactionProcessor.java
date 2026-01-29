package com.data.pipeline.processor;

import com.data.pipeline.model.Transaction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.Set;

/**
 * Processor for transaction validation and enrichment
 */
@Component
public class TransactionProcessor implements ItemProcessor<Transaction, Transaction> {

    private static final Logger logger = LoggerFactory.getLogger(TransactionProcessor.class);

    private static final Set<String> VALID_CURRENCIES = Set.of("USD", "EUR", "GBP", "JPY", "CAD");
    private static final Set<String> VALID_TYPES = Set.of("PURCHASE", "REFUND", "TRANSFER", "WITHDRAWAL", "DEPOSIT");

    @Value("${batch.transaction.max-amount:1000000}")
    private BigDecimal maxAmount;

    @Value("${batch.transaction.min-amount:0.01}")
    private BigDecimal minAmount;

    @Override
    public Transaction process(Transaction transaction) throws Exception {
        logger.debug("Processing transaction: {}", transaction.getTransactionId());

        // Validate currency
        if (!VALID_CURRENCIES.contains(transaction.getCurrency())) {
            logger.warn("Invalid currency {} for transaction {}, skipping", 
                transaction.getCurrency(), transaction.getTransactionId());
            return null;
        }

        // Validate transaction type
        String type = transaction.getType().toUpperCase();
        if (!VALID_TYPES.contains(type)) {
            logger.warn("Invalid type {} for transaction {}, skipping", 
                transaction.getType(), transaction.getTransactionId());
            return null;
        }
        transaction.setType(type);

        // Validate amount range
        if (transaction.getAmount().compareTo(minAmount) < 0 || 
            transaction.getAmount().compareTo(maxAmount) > 0) {
            logger.warn("Amount {} out of range for transaction {}, skipping", 
                transaction.getAmount(), transaction.getTransactionId());
            return null;
        }

        // Set status
        transaction.setStatus("PROCESSED");

        return transaction;
    }
}
