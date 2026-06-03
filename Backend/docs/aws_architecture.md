# VoxPilot AWS Architecture Path

This document sketches a credible production-oriented AWS path for the VoxPilot PoC.

## Target Shape

```text
Users or internal reviewers
    -> Streamlit demo UI container
    -> FastAPI service
        -> TTS engine provider
        -> S3 generated audio bucket
        -> RDS PostgreSQL run history and feedback
        -> CloudWatch metrics and logs
        -> Secrets Manager or SSM Parameter Store
```

## Compute

- Run the FastAPI service on ECS/Fargate or AWS App Runner.
- Run the Streamlit UI as a separate internal demo container, or omit it for API-only environments.
- Use separate task definitions or services for API and UI so the API can scale independently.
- Keep the API stateless except for generated asset writes and database records.

## Storage

- Store generated audio in S3.
- Use object keys based on generation run IDs.
- Return signed URLs for playback or download.
- Apply retention policies for generated assets.
- Store run history and feedback in RDS/PostgreSQL.

## TTS Engine Options

Choose the engine based on production goals:

- Amazon Polly for managed speech generation.
- A SageMaker endpoint for a model endpoint managed by the ML team.
- A Bedrock-compatible speech service if available in the target environment.
- A self-hosted TTS model service behind a private endpoint.

The FastAPI app should call the selected engine through the existing engine abstraction so API contracts and product workflows remain stable.

## Observability

- Send application logs to CloudWatch Logs.
- Emit structured request metadata: run ID, engine, latency, cache hit, success, and error class.
- Publish service metrics to CloudWatch, including request count, success rate, p95 latency, cache hit rate, feedback count, and average rating.
- Add alarms for elevated error rate, high latency, failed task health checks, and database connectivity failures.

## Secrets And Configuration

- Store secrets in AWS Secrets Manager or SSM Parameter Store.
- Inject configuration through ECS task environment variables or App Runner configuration.
- Do not commit secrets to the repository.
- Keep `.env` local only.

## CI/CD

- Use GitHub Actions to run tests on every pull request.
- Build and scan container images.
- Push images to Amazon ECR.
- Deploy API and UI services through ECS service updates, App Runner deployments, or infrastructure-as-code pipelines.
- Promote through dev, staging, and production environments with environment-specific configuration.

## Security Notes

- Use IAM least privilege for S3, RDS, CloudWatch, ECR, and Secrets Manager access.
- Keep generated audio buckets private.
- Serve generated assets through signed URLs.
- Encrypt S3 and RDS data at rest.
- Use TLS for public and internal service traffic.
- Place RDS in private subnets.
- Restrict UI access if it is meant for internal demos.
- Apply retention policies for generated assets and logs.

## Migration From Local PoC

1. Replace SQLite repository configuration with PostgreSQL.
2. Replace local generated file paths with S3 object storage.
3. Add signed URL generation to the audio response path.
4. Add CloudWatch metric emission.
5. Package API and UI as separate deployable containers.
6. Move runtime configuration and secrets into AWS-managed configuration stores.
