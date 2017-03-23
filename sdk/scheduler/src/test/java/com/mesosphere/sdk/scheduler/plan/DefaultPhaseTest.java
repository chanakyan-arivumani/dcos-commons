package com.mesosphere.sdk.scheduler.plan;

import com.mesosphere.sdk.scheduler.plan.strategy.CanaryStrategy;
import com.mesosphere.sdk.scheduler.plan.strategy.SerialStrategy;
import org.junit.Assert;
import org.junit.Test;
import org.mockito.Mockito;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;

import static org.mockito.Matchers.any;
import static org.mockito.Mockito.when;

public class DefaultPhaseTest {

    @Test
    public void testGetStatus() {
        Step step1 = Mockito.mock(DeploymentStep.class);
        Step step2 = Mockito.mock(DeploymentStep.class);

        final DefaultPhase serialPhase = new DefaultPhase(
                "serial-phase",
                Arrays.asList(step1, step2),
                new SerialStrategy<>(),
                Collections.emptyList());

        when(step1.getStatus()).thenReturn(Status.PENDING);
        when(step2.getStatus()).thenReturn(Status.WAITING);
        when(step1.isEligible(any(Collection.class))).thenReturn(true);
        when(step2.isEligible(any(Collection.class))).thenReturn(true);

        Assert.assertEquals(Status.PENDING, serialPhase.getStatus());

        when(step1.getStatus()).thenReturn(Status.WAITING);
        when(step2.getStatus()).thenReturn(Status.WAITING);
        when(step1.isEligible(any(Collection.class))).thenReturn(true);
        when(step2.isEligible(any(Collection.class))).thenReturn(true);

        final DefaultPhase canaryPhase = new DefaultPhase(
                "canary-phase",
                Arrays.asList(step1, step2),
                new CanaryStrategy(new SerialStrategy<>()),
                Collections.emptyList());

        Assert.assertEquals(Status.WAITING, canaryPhase.getStatus());
    }
}
