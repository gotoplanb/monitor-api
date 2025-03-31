"""
OpenTelemetry configuration module.
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def init_telemetry(service_name: str):
    """Initialize OpenTelemetry with FastAPI instrumentation."""
    # Create a resource with service name
    resource = Resource.create(
        {
            "service.name": service_name,
        }
    )

    # Create a tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # In test environment, use console exporter
    if os.getenv("TESTING"):
        span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    else:
        # Get OpenTelemetry collector endpoint from environment
        collector_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

        if collector_endpoint:
            # Create an OTLP exporter for the collector
            otlp_exporter = OTLPSpanExporter(
                endpoint=collector_endpoint,
                insecure=True,  # Set to False in production with proper TLS
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
        else:
            # Use console exporter for local development
            span_processor = BatchSpanProcessor(ConsoleSpanExporter())

    tracer_provider.add_span_processor(span_processor)

    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)

    return tracer_provider


def instrument_app(app, tracer_provider=None):
    """Instrument a FastAPI application with OpenTelemetry."""
    # Skip instrumentation in test environment
    if os.getenv("TESTING"):
        return

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        # Optional: Configure header capture
        http_capture_headers_server_request=["content-type", "user-agent"],
        http_capture_headers_server_response=["content-type"],
        # Optional: Configure header sanitization for sensitive data
        http_capture_headers_sanitize_fields=["authorization", "cookie", "set-cookie"],
    )
