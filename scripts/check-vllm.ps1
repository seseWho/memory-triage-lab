[CmdletBinding()]
param(
    [string]$BaseUrl = "http://localhost:8000/v1",
    [string]$Model = "qwen3-8b-awq"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking model catalog at $BaseUrl/models"
$models = Invoke-RestMethod -Uri "$BaseUrl/models" -Method Get
if ($models.data.id -notcontains $Model) {
    throw "Expected served model '$Model' was not returned by vLLM."
}

$requestBody = @{
    model = $Model
    messages = @(
        @{
            role = "user"
            content = "Return only a JSON object with property status and value ok."
        }
    )
    temperature = 0
    seed = 0
    max_tokens = 64
    response_format = @{
        type = "json_object"
    }
} | ConvertTo-Json -Depth 6

Write-Host "Checking structured chat completion"
$response = Invoke-RestMethod `
    -Uri "$BaseUrl/chat/completions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $requestBody `
    -TimeoutSec 180

$content = $response.choices[0].message.content
$parsed = $content | ConvertFrom-Json
if ($parsed.status -ne "ok") {
    throw "Unexpected structured response: $content"
}

Write-Host "vLLM checks passed for model '$Model'."

