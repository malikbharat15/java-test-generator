package com.data.pipeline.controller;

import com.data.pipeline.dto.JobExecutionRequest;
import com.data.pipeline.dto.JobExecutionResponse;
import com.data.pipeline.dto.JobStatusResponse;
import org.springframework.batch.core.*;
import org.springframework.batch.core.explore.JobExplorer;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.launch.JobOperator;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.time.LocalDateTime;
import java.util.*;

/**
 * REST API for managing batch job executions
 */
@RestController
@RequestMapping("/api/v1/jobs")
public class JobController {

    @Autowired
    private JobLauncher jobLauncher;

    @Autowired
    private JobExplorer jobExplorer;

    @Autowired
    private JobOperator jobOperator;

    @Autowired
    private JobRepository jobRepository;

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
     * Launch a batch job with optional parameters
     */
    @PostMapping("/{jobName}/launch")
    @PreAuthorize("hasRole('BATCH_OPERATOR') or hasRole('ADMIN')")
    public ResponseEntity<JobExecutionResponse> launchJob(
            @PathVariable String jobName,
            @Valid @RequestBody(required = false) JobExecutionRequest request) throws Exception {
        
        Job job = resolveJob(jobName);
        if (job == null) {
            return ResponseEntity.notFound().build();
        }

        JobParametersBuilder builder = new JobParametersBuilder();
        builder.addLong("timestamp", System.currentTimeMillis());
        
        if (request != null && request.getParameters() != null) {
            request.getParameters().forEach((key, value) -> builder.addString(key, value));
        }

        JobExecution execution = jobLauncher.run(job, builder.toJobParameters());
        
        return ResponseEntity.accepted().body(mapToResponse(execution));
    }

    /**
     * Get job execution status by execution ID
     */
    @GetMapping("/executions/{executionId}")
    @PreAuthorize("hasAnyRole('BATCH_VIEWER', 'BATCH_OPERATOR', 'ADMIN')")
    public ResponseEntity<JobExecutionResponse> getJobExecution(
            @PathVariable Long executionId) {
        
        JobExecution execution = jobExplorer.getJobExecution(executionId);
        if (execution == null) {
            return ResponseEntity.notFound().build();
        }
        
        return ResponseEntity.ok(mapToResponse(execution));
    }

    /**
     * Get all executions for a specific job
     */
    @GetMapping("/{jobName}/executions")
    @PreAuthorize("hasAnyRole('BATCH_VIEWER', 'BATCH_OPERATOR', 'ADMIN')")
    public ResponseEntity<List<JobExecutionResponse>> getJobExecutions(
            @PathVariable String jobName,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        List<JobInstance> instances = jobExplorer.findJobInstancesByJobName(jobName, page * size, size);
        List<JobExecutionResponse> responses = new ArrayList<>();
        
        for (JobInstance instance : instances) {
            List<JobExecution> executions = jobExplorer.getJobExecutions(instance);
            for (JobExecution execution : executions) {
                responses.add(mapToResponse(execution));
            }
        }
        
        return ResponseEntity.ok(responses);
    }

    /**
     * Stop a running job execution
     */
    @PostMapping("/executions/{executionId}/stop")
    @PreAuthorize("hasRole('BATCH_OPERATOR') or hasRole('ADMIN')")
    public ResponseEntity<JobStatusResponse> stopJob(
            @PathVariable Long executionId) throws Exception {
        
        boolean stopped = jobOperator.stop(executionId);
        
        JobStatusResponse response = new JobStatusResponse();
        response.setExecutionId(executionId);
        response.setStopped(stopped);
        response.setTimestamp(LocalDateTime.now());
        
        return ResponseEntity.ok(response);
    }

    /**
     * Restart a failed job execution
     */
    @PostMapping("/executions/{executionId}/restart")
    @PreAuthorize("hasRole('BATCH_OPERATOR') or hasRole('ADMIN')")
    public ResponseEntity<JobExecutionResponse> restartJob(
            @PathVariable Long executionId) throws Exception {
        
        Long newExecutionId = jobOperator.restart(executionId);
        JobExecution execution = jobExplorer.getJobExecution(newExecutionId);
        
        return ResponseEntity.accepted().body(mapToResponse(execution));
    }

    /**
     * Get list of all registered jobs
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('BATCH_VIEWER', 'BATCH_OPERATOR', 'ADMIN')")
    public ResponseEntity<List<String>> getRegisteredJobs() {
        return ResponseEntity.ok(List.of(
            "customerDataImportJob",
            "transactionProcessingJob", 
            "reportGenerationJob"
        ));
    }

    /**
     * Get running job executions
     */
    @GetMapping("/running")
    @PreAuthorize("hasAnyRole('BATCH_VIEWER', 'BATCH_OPERATOR', 'ADMIN')")
    public ResponseEntity<Set<Long>> getRunningExecutions() throws Exception {
        Set<Long> running = new HashSet<>();
        running.addAll(jobOperator.getRunningExecutions("customerDataImportJob"));
        running.addAll(jobOperator.getRunningExecutions("transactionProcessingJob"));
        running.addAll(jobOperator.getRunningExecutions("reportGenerationJob"));
        return ResponseEntity.ok(running);
    }

    private Job resolveJob(String jobName) {
        switch (jobName) {
            case "customerDataImportJob":
                return customerDataImportJob;
            case "transactionProcessingJob":
                return transactionProcessingJob;
            case "reportGenerationJob":
                return reportGenerationJob;
            default:
                return null;
        }
    }

    private JobExecutionResponse mapToResponse(JobExecution execution) {
        JobExecutionResponse response = new JobExecutionResponse();
        response.setExecutionId(execution.getId());
        response.setJobName(execution.getJobInstance().getJobName());
        response.setStatus(execution.getStatus().toString());
        response.setExitCode(execution.getExitStatus().getExitCode());
        response.setStartTime(execution.getStartTime());
        response.setEndTime(execution.getEndTime());
        response.setCreateTime(execution.getCreateTime());
        
        Map<String, String> params = new HashMap<>();
        execution.getJobParameters().getParameters().forEach((key, value) -> 
            params.put(key, value.getValue().toString()));
        response.setParameters(params);
        
        return response;
    }
}
