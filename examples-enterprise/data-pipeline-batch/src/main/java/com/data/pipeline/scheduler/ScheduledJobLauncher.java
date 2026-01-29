package com.data.pipeline.scheduler;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.*;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * Scheduled job launcher for automated batch processing
 */
@Component
public class ScheduledJobLauncher {

    private static final Logger logger = LoggerFactory.getLogger(ScheduledJobLauncher.class);

    @Autowired
    private JobLauncher jobLauncher;

    @Autowired
    @Qualifier("customerDataImportJob")
    private Job customerDataImportJob;

    @Autowired
    @Qualifier("transactionProcessingJob")
    private Job transactionProcessingJob;

    @Autowired
    @Qualifier("reportGenerationJob")
    private Job reportGenerationJob;

    /**
     * Import customer data daily at 2 AM
     */
    @Scheduled(cron = "0 0 2 * * ?")
    public void runCustomerDataImport() {
        logger.info("Starting scheduled customer data import job");
        try {
            JobParameters params = new JobParametersBuilder()
                    .addString("date", LocalDate.now().format(DateTimeFormatter.ISO_DATE))
                    .addLong("timestamp", System.currentTimeMillis())
                    .addString("source", "scheduled")
                    .toJobParameters();

            JobExecution execution = jobLauncher.run(customerDataImportJob, params);
            logger.info("Customer data import completed with status: {}", execution.getStatus());
        } catch (Exception e) {
            logger.error("Failed to execute customer data import job", e);
        }
    }

    /**
     * Process transactions every hour
     */
    @Scheduled(cron = "0 0 * * * ?")
    public void runTransactionProcessing() {
        logger.info("Starting scheduled transaction processing job");
        try {
            JobParameters params = new JobParametersBuilder()
                    .addString("date", LocalDate.now().format(DateTimeFormatter.ISO_DATE))
                    .addLong("timestamp", System.currentTimeMillis())
                    .addString("source", "scheduled")
                    .toJobParameters();

            JobExecution execution = jobLauncher.run(transactionProcessingJob, params);
            logger.info("Transaction processing completed with status: {}", execution.getStatus());
        } catch (Exception e) {
            logger.error("Failed to execute transaction processing job", e);
        }
    }

    /**
     * Generate daily report at 6 AM
     */
    @Scheduled(cron = "0 0 6 * * ?")
    public void runDailyReportGeneration() {
        logger.info("Starting scheduled daily report generation job");
        try {
            JobParameters params = new JobParametersBuilder()
                    .addString("reportDate", LocalDate.now().minusDays(1).format(DateTimeFormatter.ISO_DATE))
                    .addLong("timestamp", System.currentTimeMillis())
                    .addString("source", "scheduled")
                    .toJobParameters();

            JobExecution execution = jobLauncher.run(reportGenerationJob, params);
            logger.info("Daily report generation completed with status: {}", execution.getStatus());
        } catch (Exception e) {
            logger.error("Failed to execute daily report generation job", e);
        }
    }

    /**
     * Generate weekly report every Monday at 7 AM
     */
    @Scheduled(cron = "0 0 7 ? * MON")
    public void runWeeklyReportGeneration() {
        logger.info("Starting scheduled weekly report generation job");
        try {
            JobParameters params = new JobParametersBuilder()
                    .addString("reportType", "weekly")
                    .addString("weekStartDate", LocalDate.now().minusWeeks(1).format(DateTimeFormatter.ISO_DATE))
                    .addString("weekEndDate", LocalDate.now().minusDays(1).format(DateTimeFormatter.ISO_DATE))
                    .addLong("timestamp", System.currentTimeMillis())
                    .addString("source", "scheduled")
                    .toJobParameters();

            JobExecution execution = jobLauncher.run(reportGenerationJob, params);
            logger.info("Weekly report generation completed with status: {}", execution.getStatus());
        } catch (Exception e) {
            logger.error("Failed to execute weekly report generation job", e);
        }
    }
}
