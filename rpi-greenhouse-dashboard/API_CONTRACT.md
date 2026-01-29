# IoT Dashboard API – DEV Notes

## Frontend Integration

In final build the frontend is served from backend and communicate though `/api/*` endpoints.
For development a **dev proxy** is used to forward API requests to the backend.
- During development, the frontend dev server proxies `/api/*` to the backend running on `localhost`
- The backend should listen on `localhost` (e.g. `127.0.0.1`)
- No CORS configuration is required for local development
- API routes are defined **without** the `/api` prefix on the backend

The target backend route is specified in `vite.config.ts`.

---

## JSON Format Conventions

* All timestamps are **Unix epoch milliseconds** (`number`).
* If an RPI is **disconnected**, return:

    * `connectionStatus: "disconnected"`
    * `currTemperature: null`
    * `currHumidity: null`

This avoids confusing the UI with stale values.

---

## Types (Reference)

### Range

```json
{
  "min": 18,
  "max": 25
}
```

### Plant

```json
{
  "id": "string",
  "commonName": "string",
  "scientificName": "string",
  "imageUrl": "string",
  "temperature": {
    "warning": { "min": 0, "max": 0 },
    "critical": { "min": 0, "max": 0 }
  },
  "humidity": {
    "warning": { "min": 0, "max": 0 },
    "critical": { "min": 0, "max": 0 }
  }
}
```

* `id`, `commonName`, `scientificName`, `imageUrl`, `temperature`, and `humidity` **must not be null**

---

### SensorData (Full RPI Object)

```json
{
  "id": 1,
  "rpiName": "Greenhouse #1",
  "plant": null,
  "currTemperature": 22.4,
  "currHumidity": 61.2,
  "connectionStatus": "connected"
}
```

#### Constraints

* `id` **must not be null**
* `rpiName` **must not be null or empty**
* `connectionStatus` is one of:

  ```typescript
  "connected" | "disconnected"
  ```
* When `connectionStatus === "disconnected"`:

  ```json
  "currTemperature": null,
  "currHumidity": null
  ```

---

## Endpoints

### GET /rpis

Returns all registered RPIs.

#### Response

```json
[
  {
    "id": 1,
    "rpiName": "Greenhouse #1",
    "plant": { /* Plant object or null */ },
    "currTemperature": 21.9,
    "currHumidity": 58.3,
    "connectionStatus": "connected"
  }
]
```

---

### PUT /rpis/{id}

Update RPI data.

#### Request (partial update allowed)

```json
{
  "rpiName": "Living Room RPI",
  "plant": { /* Plant object or null */ }
}
```

* Any omitted fields remain unchanged
* `rpiName` must not be empty if provided
* If `plant` is set, the update should not change it to `null`

#### Response

```json
{
  "id": 1,
  "rpiName": "Living Room RPI",
  "plant": { /* Plant or null */ },
  "currTemperature": 23.1,
  "currHumidity": 55.0,
  "connectionStatus": "connected"
}
```

---

### GET /rpis/readings

Polling endpoint for live sensor data.

#### Response

```json
[
  {
    "id": 1,
    "currTemperature": 22.1,
    "currHumidity": 57.8,
    "connectionStatus": "connected"
  }
]
```

#### Disconnected example

```json
{
  "id": 1,
  "currTemperature": null,
  "currHumidity": null,
  "connectionStatus": "disconnected"
}
```

* `id` **must not be null**
* Temperature and humidity **must be null when disconnected**

---

### GET /rpis/{id}/history

Returns historical sensor data for charts.

#### Response

```json
{
  "measurements": [
    {
      "timestamp": 1700000000000,
      "temperature": 22.4,
      "humidity": 60.1
    },
    // ...more entries
  ]
}
```

#### Constraints

* `timestamp`, `temperature`, and `humidity` **must not be null**
* backend **should group or filter** data points if the sample is too large
* If no history exists:

```json
{
  "measurements": []
}
```

---


### GET /plants?q=search

Search plants.

#### Response

```json
[
  {
    "id": "string",
    "commonName": "Basil",
    "scientificName": "Ocimum basilicum",
    "imageUrl": "https://...",
    "temperature": { /* Range sets */ },
    "humidity": { /* Range sets */ }
  }
]
```

---

## Notes / Assumptions

* History data is assumed to **never contain null values**
* The backend is responsible for clearing current readings on disconnect
* `connectionStatus` is the single source of truth for connection state

---

If any endpoint behavior differs, update this doc accordingly.
