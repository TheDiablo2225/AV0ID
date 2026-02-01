import json

def stream_cadets_events(file_path):
    """
    Generator that yields parsed CADETS events one by one.
    """
    with open(file_path, "r") as f:
        for line in f:
            try:
                record = json.loads(line)
                event = record["datum"]["com.bbn.tc.schema.avro.cdm18.Event"]

                yield {
                    "time": event.get("timestampNanos"),
                    "subject": event["subject"]["com.bbn.tc.schema.avro.cdm18.UUID"],
                    "object": event.get("predicateObject", {}).get(
                        "com.bbn.tc.schema.avro.cdm18.UUID"
                    ),
                    "event_type": event.get("type")
                }
            except Exception:
                continue
