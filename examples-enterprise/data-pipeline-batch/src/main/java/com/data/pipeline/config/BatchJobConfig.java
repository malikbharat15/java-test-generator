package com.data.pipeline.config;

import com.data.pipeline.model.Customer;
import com.data.pipeline.model.Transaction;
import com.data.pipeline.processor.CustomerProcessor;
import com.data.pipeline.processor.TransactionProcessor;
import com.data.pipeline.listener.JobCompletionListener;
import org.springframework.batch.core.*;
import org.springframework.batch.core.configuration.annotation.JobBuilderFactory;
import org.springframework.batch.core.configuration.annotation.StepBuilderFactory;
import org.springframework.batch.core.launch.support.RunIdIncrementer;
import org.springframework.batch.item.database.JdbcBatchItemWriter;
import org.springframework.batch.item.database.builder.JdbcBatchItemWriterBuilder;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.batch.item.file.builder.FlatFileItemReaderBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.FileSystemResource;

import javax.sql.DataSource;

/**
 * Configuration for batch jobs
 */
@Configuration
public class BatchJobConfig {

    @Autowired
    private JobBuilderFactory jobBuilderFactory;

    @Autowired
    private StepBuilderFactory stepBuilderFactory;

    @Autowired
    private DataSource dataSource;

    @Value("${batch.input.customer-file}")
    private String customerFilePath;

    @Value("${batch.input.transaction-file}")
    private String transactionFilePath;

    @Value("${batch.chunk-size:100}")
    private int chunkSize;

    // ==================== Customer Data Import Job ====================

    @Bean
    public Job customerDataImportJob(Step customerImportStep, JobCompletionListener listener) {
        return jobBuilderFactory.get("customerDataImportJob")
                .incrementer(new RunIdIncrementer())
                .listener(listener)
                .flow(customerImportStep)
                .end()
                .build();
    }

    @Bean
    public Step customerImportStep(FlatFileItemReader<Customer> customerReader,
                                   CustomerProcessor customerProcessor,
                                   JdbcBatchItemWriter<Customer> customerWriter) {
        return stepBuilderFactory.get("customerImportStep")
                .<Customer, Customer>chunk(chunkSize)
                .reader(customerReader)
                .processor(customerProcessor)
                .writer(customerWriter)
                .faultTolerant()
                .skipLimit(10)
                .skip(Exception.class)
                .build();
    }

    @Bean
    public FlatFileItemReader<Customer> customerReader() {
        return new FlatFileItemReaderBuilder<Customer>()
                .name("customerReader")
                .resource(new FileSystemResource(customerFilePath))
                .delimited()
                .names("id", "firstName", "lastName", "email", "phone", "tier")
                .targetType(Customer.class)
                .linesToSkip(1)
                .build();
    }

    @Bean
    public JdbcBatchItemWriter<Customer> customerWriter() {
        return new JdbcBatchItemWriterBuilder<Customer>()
                .sql("INSERT INTO customers (id, first_name, last_name, email, phone, tier, created_at) " +
                     "VALUES (:id, :firstName, :lastName, :email, :phone, :tier, CURRENT_TIMESTAMP) " +
                     "ON CONFLICT (id) DO UPDATE SET first_name = :firstName, last_name = :lastName, " +
                     "email = :email, phone = :phone, tier = :tier")
                .dataSource(dataSource)
                .beanMapped()
                .build();
    }

    // ==================== Transaction Processing Job ====================

    @Bean
    public Job transactionProcessingJob(Step transactionProcessStep, Step aggregationStep, 
                                        JobCompletionListener listener) {
        return jobBuilderFactory.get("transactionProcessingJob")
                .incrementer(new RunIdIncrementer())
                .listener(listener)
                .start(transactionProcessStep)
                .next(aggregationStep)
                .build();
    }

    @Bean
    public Step transactionProcessStep(FlatFileItemReader<Transaction> transactionReader,
                                       TransactionProcessor transactionProcessor,
                                       JdbcBatchItemWriter<Transaction> transactionWriter) {
        return stepBuilderFactory.get("transactionProcessStep")
                .<Transaction, Transaction>chunk(chunkSize)
                .reader(transactionReader)
                .processor(transactionProcessor)
                .writer(transactionWriter)
                .build();
    }

    @Bean
    public Step aggregationStep() {
        return stepBuilderFactory.get("aggregationStep")
                .tasklet((contribution, chunkContext) -> {
                    // Aggregate transaction data
                    return RepeatStatus.FINISHED;
                })
                .build();
    }

    @Bean
    public FlatFileItemReader<Transaction> transactionReader() {
        return new FlatFileItemReaderBuilder<Transaction>()
                .name("transactionReader")
                .resource(new FileSystemResource(transactionFilePath))
                .delimited()
                .names("transactionId", "customerId", "amount", "currency", "type", "timestamp")
                .targetType(Transaction.class)
                .linesToSkip(1)
                .build();
    }

    @Bean
    public JdbcBatchItemWriter<Transaction> transactionWriter() {
        return new JdbcBatchItemWriterBuilder<Transaction>()
                .sql("INSERT INTO transactions (transaction_id, customer_id, amount, currency, type, " +
                     "transaction_timestamp, processed_at) VALUES (:transactionId, :customerId, :amount, " +
                     ":currency, :type, :timestamp, CURRENT_TIMESTAMP)")
                .dataSource(dataSource)
                .beanMapped()
                .build();
    }

    // ==================== Report Generation Job ====================

    @Bean
    public Job reportGenerationJob(Step dailySummaryStep, Step sendReportStep,
                                   JobCompletionListener listener) {
        return jobBuilderFactory.get("reportGenerationJob")
                .incrementer(new RunIdIncrementer())
                .listener(listener)
                .start(dailySummaryStep)
                .next(sendReportStep)
                .build();
    }

    @Bean
    public Step dailySummaryStep() {
        return stepBuilderFactory.get("dailySummaryStep")
                .tasklet((contribution, chunkContext) -> {
                    // Generate daily summary report
                    return RepeatStatus.FINISHED;
                })
                .build();
    }

    @Bean
    public Step sendReportStep() {
        return stepBuilderFactory.get("sendReportStep")
                .tasklet((contribution, chunkContext) -> {
                    // Send report via email/S3/FTP
                    return RepeatStatus.FINISHED;
                })
                .build();
    }
}
