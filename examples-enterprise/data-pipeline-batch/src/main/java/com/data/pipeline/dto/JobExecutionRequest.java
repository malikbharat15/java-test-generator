package com.data.pipeline.dto;

import javax.validation.constraints.NotNull;
import java.util.Map;

/**
 * Request DTO for launching batch jobs with parameters
 */
public class JobExecutionRequest {

    /**
     * Optional job parameters as key-value pairs
     */
    private Map<String, String> parameters;

    /**
     * Priority level for the job execution
     */
    private String priority;

    /**
     * Force run even if another instance is running
     */
    private boolean forceRun;

    /**
     * Callback URL for job completion notification
     */
    private String callbackUrl;

    public Map<String, String> getParameters() {
        return parameters;
    }

    public void setParameters(Map<String, String> parameters) {
        this.parameters = parameters;
    }

    public String getPriority() {
        return priority;
    }

    public void setPriority(String priority) {
        this.priority = priority;
    }

    public boolean isForceRun() {
        return forceRun;
    }

    public void setForceRun(boolean forceRun) {
        this.forceRun = forceRun;
    }

    public String getCallbackUrl() {
        return callbackUrl;
    }

    public void setCallbackUrl(String callbackUrl) {
        this.callbackUrl = callbackUrl;
    }
}
