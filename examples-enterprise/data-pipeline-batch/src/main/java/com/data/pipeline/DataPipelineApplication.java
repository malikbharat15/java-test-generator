package com.data.pipeline;

import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Data Pipeline Application
 * Spring Batch with scheduled jobs and REST API for job management
 */
@SpringBootApplication
@EnableBatchProcessing
@EnableScheduling
public class DataPipelineApplication {
    public static void main(String[] args) {
        SpringApplication.run(DataPipelineApplication.class, args);
    }
}
