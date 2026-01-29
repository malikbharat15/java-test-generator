package com.data.pipeline.listener;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobExecutionListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/**
 * Listener for job completion events
 */
@Component
public class JobCompletionListener implements JobExecutionListener {

    private static final Logger logger = LoggerFactory.getLogger(JobCompletionListener.class);

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Override
    public void beforeJob(JobExecution jobExecution) {
        logger.info("Job {} starting with parameters: {}", 
            jobExecution.getJobInstance().getJobName(),
            jobExecution.getJobParameters());
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        String jobName = jobExecution.getJobInstance().getJobName();
        BatchStatus status = jobExecution.getStatus();
        
        logger.info("Job {} finished with status: {}", jobName, status);

        if (status == BatchStatus.COMPLETED) {
            logJobStatistics(jobName);
        } else if (status == BatchStatus.FAILED) {
            logger.error("Job {} failed with exceptions: {}", 
                jobName, jobExecution.getAllFailureExceptions());
        }
    }

    private void logJobStatistics(String jobName) {
        try {
            if ("customerDataImportJob".equals(jobName)) {
                Long count = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM customers WHERE created_at > CURRENT_DATE", Long.class);
                logger.info("Customers imported today: {}", count);
            } else if ("transactionProcessingJob".equals(jobName)) {
                Long count = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM transactions WHERE processed_at > CURRENT_DATE", Long.class);
                logger.info("Transactions processed today: {}", count);
            }
        } catch (Exception e) {
            logger.warn("Could not retrieve job statistics", e);
        }
    }
}
