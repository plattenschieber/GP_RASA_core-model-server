package io.archilab.gpchatbot;

import com.atlassian.bamboo.specs.api.BambooSpec;
import com.atlassian.bamboo.specs.api.builders.BambooKey;
import com.atlassian.bamboo.specs.api.builders.BambooOid;
import com.atlassian.bamboo.specs.api.builders.permission.PermissionType;
import com.atlassian.bamboo.specs.api.builders.permission.Permissions;
import com.atlassian.bamboo.specs.api.builders.permission.PlanPermissions;
import com.atlassian.bamboo.specs.api.builders.plan.Job;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import com.atlassian.bamboo.specs.api.builders.plan.PlanIdentifier;
import com.atlassian.bamboo.specs.api.builders.plan.Stage;
import com.atlassian.bamboo.specs.api.builders.plan.artifact.Artifact;
import com.atlassian.bamboo.specs.api.builders.plan.branches.BranchCleanup;
import com.atlassian.bamboo.specs.api.builders.plan.branches.PlanBranchManagement;
import com.atlassian.bamboo.specs.api.builders.plan.configuration.ConcurrentBuilds;
import com.atlassian.bamboo.specs.api.builders.project.Project;
import com.atlassian.bamboo.specs.api.builders.requirement.Requirement;
import com.atlassian.bamboo.specs.builders.task.CheckoutItem;
import com.atlassian.bamboo.specs.builders.task.DockerBuildImageTask;
import com.atlassian.bamboo.specs.builders.task.DockerPushImageTask;
import com.atlassian.bamboo.specs.builders.task.InjectVariablesTask;
import com.atlassian.bamboo.specs.builders.task.ScriptTask;
import com.atlassian.bamboo.specs.builders.task.VcsCheckoutTask;
import com.atlassian.bamboo.specs.builders.trigger.BitbucketServerTrigger;
import com.atlassian.bamboo.specs.model.task.InjectVariablesScope;
import com.atlassian.bamboo.specs.util.BambooServer;

@BambooSpec
public class PlanSpec {

  public Plan plan() {
    final Plan plan = new Plan(new Project()
        .oid(new BambooOid("ky5ricqu8qv5"))
        .key(new BambooKey("CHAT"))
        .name("Chatbot"),
        "core-model-server",
        new BambooKey("CMS"))
        .oid(new BambooOid("kxw2ardmf1mx"))
        .pluginConfigurations(new ConcurrentBuilds()
            .useSystemWideDefault(false))
        .stages(new Stage("Default Stage")
            .jobs(new Job("Default Job",
                new BambooKey("JOB1"))
                .artifacts(
                    new Artifact().name("docker-compose")
                        .copyPattern("docker-compose.yaml")
                        .location("./docker").shared(true).required(true))
                .tasks(
                    new VcsCheckoutTask()
                        .description("Checkout the repository")
                        .checkoutItems(new CheckoutItem()
                            .defaultRepository()),
                    new ScriptTask().description(
                        "Create commit hash variable file")
                        .inlineBody("echo \"commit-hash=$(date +%s%N)\" > ./commit-hash"),
                    new InjectVariablesTask()
                        .description("Inject the commit hash variable")
                        .path("./commit-hash")
                        .namespace("inject")
                        .scope(InjectVariablesScope.RESULT),
                    new DockerBuildImageTask()
                        .description("Build the Docker image")
                        .imageName("docker.nexus.gpchatbot.archi-lab.io/chatbot/core-model-server")
                        .useCache(true)
                        .dockerfileInWorkingDir(),
                    new ScriptTask().description(
                        "Tag the Docker image with commit hash")
                        .inlineBody(
                            "docker tag docker.nexus.gpchatbot.archi-lab.io/chatbot/core-model-server docker.nexus.gpchatbot.archi-lab.io/chatbot/core-model-server:${bamboo.inject.commit-hash}"),
                    new DockerPushImageTask()
                        .customRegistryImage(
                            "docker.nexus.gpchatbot.archi-lab.io/chatbot/core-model-server")
                        .defaultAuthentication(),
                    new DockerPushImageTask()
                        .customRegistryImage(
                            "docker.nexus.gpchatbot.archi-lab.io/chatbot/core-model-server:${bamboo.inject.commit-hash}")
                        .defaultAuthentication(),
                    new ScriptTask().description(
                        "Remove old images from Nexus Docker repository")
                        .inlineBody(
                            "echo \"# Nexus Credentials\\nnexus_host = \\\"https://nexus.gpchatbot.archi-lab.io\\\"\\nnexus_username = \\\"bamboo\\\"\\nnexus_password = \\\"gpchatbot\\\"\\nnexus_repository = \\\"docker-hosted\\\"\" > .credentials\nnexus-cli image delete -name chatbot/core-model-server -keep 21"))
                .requirements(new Requirement(
                    "system.builder.command.nexus-cli"))))
        .linkedRepositories("core-model-server (master)")
        .triggers(new BitbucketServerTrigger())
        .planBranchManagement(new PlanBranchManagement()
            .delete(new BranchCleanup())
            .notificationForCommitters());
    return plan;
  }

  public PlanPermissions planPermission() {
    final PlanPermissions planPermission = new PlanPermissions(new PlanIdentifier("CHAT", "CMS"))
        .permissions(new Permissions()
            .userPermissions("bamboo", PermissionType.EDIT, PermissionType.VIEW,
                PermissionType.ADMIN, PermissionType.CLONE, PermissionType.BUILD)
            .loggedInUserPermissions(PermissionType.VIEW)
            .anonymousUserPermissionView());
    return planPermission;
  }

  public static void main(String... argv) {
    //By default credentials are read from the '.credentials' file.
    BambooServer bambooServer = new BambooServer("https://bamboo.gpchatbot.archi-lab.io");
    final PlanSpec planSpec = new PlanSpec();

    final Plan plan = planSpec.plan();
    bambooServer.publish(plan);

    final PlanPermissions planPermission = planSpec.planPermission();
    bambooServer.publish(planPermission);
  }
}