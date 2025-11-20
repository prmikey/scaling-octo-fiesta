# API Integration Guide

This guide explains how to integrate your actual Dell Tech Direct and Lenovo API files with this application.

## Where to Place Your API Files

Create the following directory structure and place your API documentation files:

```
VendorWarrantyManager/
└── ApiDocs/
    ├── dell-tech-direct/
    │   ├── swagger.json (or OpenAPI spec)
    │   ├── endpoints.md
    │   └── sample-requests.json
    └── lenovo/
        ├── swagger.json (or OpenAPI spec)
        ├── endpoints.md
        └── sample-requests.json
```

## Common API File Types

Your API files might be in one of these formats:

1. **OpenAPI/Swagger** (`.json`, `.yaml`)
2. **Postman Collection** (`.json`)
3. **WADL** (Web Application Description Language)
4. **API Blueprint** (`.apib`)
5. **RAML** (RESTful API Modeling Language)
6. **Simple documentation** (`.pdf`, `.md`, `.docx`)

## Integration Steps

### Step 1: Understand Your API Structure

Review your API documentation and identify:

1. **Base URL**: The root URL for all API calls
2. **Authentication Method**:
   - Bearer Token
   - API Key
   - OAuth 2.0
   - Basic Auth
3. **Endpoints**: URLs for each operation:
   - Login/Authentication
   - Get Claims
   - Create Claim
   - Check Warranty
4. **Request/Response Format**: JSON structure for each endpoint

### Step 2: Update Service Classes

#### Example: Dell Tech Direct API Integration

Suppose your Dell API documentation shows:

**Base URL**: `https://api.techdirect.dell.com/v1`

**Authentication**:
```json
POST /auth/token
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "grant_type": "password",
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Get Claims**:
```json
GET /claims?userId={userId}&status={status}

Response:
{
  "claims": [
    {
      "id": "CLM-123456",
      "serviceTag": "ABC1234",
      "description": "Screen broken",
      "status": "Open",
      "createdBy": "user@example.com",
      "createdDate": "2025-11-19T10:00:00Z"
    }
  ]
}
```

**Update `DellApiService.cs`**:

```csharp
namespace VendorWarrantyManager.Services
{
    public class DellApiService : IVendorApiService
    {
        private readonly HttpClient _httpClient;
        private string? _authToken;
        private string? _currentUser;

        // Updated from your API docs
        private const string BASE_URL = "https://api.techdirect.dell.com/v1";
        private const string AUTH_ENDPOINT = "/auth/token";
        private const string CLAIMS_ENDPOINT = "/claims";
        private const string WARRANTY_ENDPOINT = "/warranty/check";

        // If your API requires client credentials
        private const string CLIENT_ID = "your_client_id";  // Move to config!
        private const string CLIENT_SECRET = "your_client_secret";  // Move to config!

        public DellApiService(HttpClient httpClient)
        {
            _httpClient = httpClient;
            _httpClient.BaseAddress = new Uri(BASE_URL);
        }

        public async Task<bool> AuthenticateAsync(string username, string password)
        {
            try
            {
                // Updated based on actual API
                var loginRequest = new
                {
                    client_id = CLIENT_ID,
                    client_secret = CLIENT_SECRET,
                    grant_type = "password",
                    username = username,
                    password = password
                };

                var json = JsonConvert.SerializeObject(loginRequest);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync(AUTH_ENDPOINT, content);

                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();

                    // Parse actual response structure
                    var authResponse = JsonConvert.DeserializeObject<DellAuthResponse>(responseContent);

                    _authToken = authResponse?.AccessToken;
                    _currentUser = username;

                    _httpClient.DefaultRequestHeaders.Authorization =
                        new AuthenticationHeaderValue("Bearer", _authToken);

                    return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Dell Auth Error: {ex.Message}");
                return false;
            }
        }

        public async Task<List<Claim>> GetClaimsAsync(string? filterByUser = null)
        {
            try
            {
                var user = filterByUser ?? _currentUser;

                // Updated based on actual API query parameters
                var endpoint = $"{CLAIMS_ENDPOINT}?userId={user}&status=all";

                var response = await _httpClient.GetAsync(endpoint);

                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();

                    // Parse actual response structure
                    var apiResponse = JsonConvert.DeserializeObject<DellClaimsResponse>(content);

                    // Map API model to our model
                    var claims = apiResponse?.Claims?.Select(c => new Claim
                    {
                        ClaimId = c.Id,
                        ServiceTag = c.ServiceTag,
                        Description = c.Description,
                        Status = c.Status,
                        CreatedBy = c.CreatedBy,
                        CreatedDate = DateTime.Parse(c.CreatedDate),
                        Vendor = VendorType.Dell
                    }).ToList();

                    return claims ?? new List<Claim>();
                }

                return new List<Claim>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Dell Get Claims Error: {ex.Message}");
                return new List<Claim>();
            }
        }

        // ... other methods
    }

    // Add response models matching your API
    public class DellAuthResponse
    {
        [JsonProperty("access_token")]
        public string AccessToken { get; set; } = string.Empty;

        [JsonProperty("token_type")]
        public string TokenType { get; set; } = string.Empty;

        [JsonProperty("expires_in")]
        public int ExpiresIn { get; set; }
    }

    public class DellClaimsResponse
    {
        [JsonProperty("claims")]
        public List<DellClaim> Claims { get; set; } = new List<DellClaim>();
    }

    public class DellClaim
    {
        [JsonProperty("id")]
        public string Id { get; set; } = string.Empty;

        [JsonProperty("serviceTag")]
        public string ServiceTag { get; set; } = string.Empty;

        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;

        [JsonProperty("status")]
        public string Status { get; set; } = string.Empty;

        [JsonProperty("createdBy")]
        public string CreatedBy { get; set; } = string.Empty;

        [JsonProperty("createdDate")]
        public string CreatedDate { get; set; } = string.Empty;
    }
}
```

### Step 3: Handle Different Authentication Methods

#### Bearer Token (Current Implementation)
```csharp
_httpClient.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", token);
```

#### API Key in Header
```csharp
_httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
```

#### API Key in Query String
```csharp
var endpoint = $"{CLAIMS_ENDPOINT}?apiKey={apiKey}&userId={user}";
```

#### OAuth 2.0
```csharp
// Use a library like IdentityModel
var tokenClient = new TokenClient(
    tokenEndpoint,
    clientId,
    clientSecret);

var tokenResponse = await tokenClient.RequestResourceOwnerPasswordAsync(
    username,
    password,
    scope);

_authToken = tokenResponse.AccessToken;
```

### Step 4: Test Each Endpoint

Create a test file to verify each endpoint works:

```csharp
// Create Tests/DellApiTests.cs
public class DellApiTests
{
    [Fact]
    public async Task TestAuthentication()
    {
        var httpClient = new HttpClient();
        var service = new DellApiService(httpClient);

        var result = await service.AuthenticateAsync("test@example.com", "password");

        Assert.True(result);
    }

    [Fact]
    public async Task TestGetClaims()
    {
        // ... test implementation
    }
}
```

### Step 5: Handle API-Specific Requirements

#### Image Upload for Dell

If Dell requires specific image format/encoding:

```csharp
public async Task<Claim> CreateClaimAsync(CreateClaimRequest request)
{
    var formContent = new MultipartFormDataContent();

    // Add claim data
    formContent.Add(new StringContent(request.ServiceTag), "serviceTag");
    formContent.Add(new StringContent(request.Description), "description");

    // Add images with specific requirements
    for (int i = 0; i < request.Images.Count; i++)
    {
        var imageContent = new ByteArrayContent(request.Images[i]);

        // Set content type based on API requirements
        imageContent.Headers.ContentType = MediaTypeHeaderValue.Parse("image/jpeg");

        // Use parameter name from API docs
        formContent.Add(imageContent, "attachments", $"image_{i}.jpg");
    }

    var response = await _httpClient.PostAsync("/claims", formContent);

    // ... handle response
}
```

### Step 6: Error Handling

Add proper error handling based on API error responses:

```csharp
if (!response.IsSuccessStatusCode)
{
    var errorContent = await response.Content.ReadAsStringAsync();
    var error = JsonConvert.DeserializeObject<ApiError>(errorContent);

    throw new ApiException($"API Error: {error.Message} (Code: {error.Code})");
}

public class ApiError
{
    [JsonProperty("error")]
    public string Code { get; set; } = string.Empty;

    [JsonProperty("message")]
    public string Message { get; set; } = string.Empty;

    [JsonProperty("details")]
    public string Details { get; set; } = string.Empty;
}
```

## Configuration Management

Don't hardcode credentials! Use configuration files:

### Create `appsettings.json`:

```json
{
  "Dell": {
    "BaseUrl": "https://api.techdirect.dell.com/v1",
    "ClientId": "your_client_id",
    "ClientSecret": "your_client_secret"
  },
  "Lenovo": {
    "BaseUrl": "https://api.lenovo.com/v1",
    "ApiKey": "your_api_key"
  }
}
```

### Load configuration in `App.xaml.cs`:

```csharp
using Microsoft.Extensions.Configuration;

protected override void OnStartup(StartupEventArgs e)
{
    base.OnStartup(e);

    var configuration = new ConfigurationBuilder()
        .SetBasePath(Directory.GetCurrentDirectory())
        .AddJsonFile("appsettings.json", optional: false)
        .Build();

    var serviceCollection = new ServiceCollection();
    ConfigureServices(serviceCollection, configuration);
    ServiceProvider = serviceCollection.BuildServiceProvider();
}

private void ConfigureServices(IServiceCollection services, IConfiguration configuration)
{
    services.Configure<DellSettings>(configuration.GetSection("Dell"));
    services.Configure<LenovoSettings>(configuration.GetSection("Lenovo"));

    services.AddHttpClient<DellApiService>();
    services.AddHttpClient<LenovoApiService>();

    services.AddTransient<DellApiService>();
    services.AddTransient<LenovoApiService>();
}
```

## Need Help?

1. Share your API documentation files in the `ApiDocs/` folder
2. Provide example requests/responses
3. Note any specific authentication requirements
4. Mention any rate limiting or special headers required

With this information, the service classes can be precisely tailored to your actual APIs.
