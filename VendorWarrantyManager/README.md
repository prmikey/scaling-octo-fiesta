# Vendor Warranty Manager

A C# WPF desktop application for managing warranty claims across multiple vendors (Dell Tech Direct and Lenovo).

## Features

- **Multi-Vendor Support**: Connect to Dell Tech Direct and Lenovo APIs
- **User Authentication**: Secure login with vendor-specific credentials
- **Claims Dashboard**: View and filter claims by user
- **Warranty Checker**: Check warranty status by service tag/serial number
- **Claim Creation**: Create new claims with:
  - Service tag/serial number
  - Issue description
  - Part numbers (optional)
  - Image attachments (Dell: 1-8 required, Lenovo: optional)

## Requirements

- .NET 6.0 or later
- Windows OS
- Visual Studio 2022 (or VS Code with C# extension)
- API credentials for Dell Tech Direct and/or Lenovo

## Project Structure

```
VendorWarrantyManager/
├── Models/                 # Data models
│   ├── VendorType.cs
│   ├── UserCredentials.cs
│   ├── Claim.cs
│   ├── WarrantyInfo.cs
│   └── CreateClaimRequest.cs
├── Services/              # API services
│   ├── IVendorApiService.cs
│   ├── DellApiService.cs
│   └── LenovoApiService.cs
├── Views/                 # WPF windows
│   ├── LoginWindow.xaml
│   ├── DashboardWindow.xaml
│   ├── WarrantyCheckerWindow.xaml
│   └── ClaimMakerWindow.xaml
└── App.xaml              # Application entry point
```

## API Integration Setup

### Step 1: Update API Endpoints

The application uses placeholder API endpoints. You need to update them with actual endpoints from your API documentation.

#### For Dell Tech Direct API:

Open `Services/DellApiService.cs` and update:

```csharp
private const string BASE_URL = "https://techdirect.dell.com/api";  // Replace with actual base URL
private const string AUTH_ENDPOINT = "/auth/login";                 // Replace with actual auth endpoint
private const string CLAIMS_ENDPOINT = "/claims";                   // Replace with actual claims endpoint
private const string WARRANTY_ENDPOINT = "/warranty";               // Replace with actual warranty endpoint
```

#### For Lenovo API:

Open `Services/LenovoApiService.cs` and update:

```csharp
private const string BASE_URL = "https://support.lenovo.com/api";  // Replace with actual base URL
private const string AUTH_ENDPOINT = "/auth/login";                 // Replace with actual auth endpoint
private const string CLAIMS_ENDPOINT = "/claims";                   // Replace with actual claims endpoint
private const string WARRANTY_ENDPOINT = "/warranty";               // Replace with actual warranty endpoint
```

### Step 2: Update API Request/Response Models

The API services use generic JSON serialization. You may need to adjust the request/response models based on your actual API specifications.

Review and update the following methods in both `DellApiService.cs` and `LenovoApiService.cs`:

1. **Authentication (`AuthenticateAsync`)**: Ensure the login request payload matches your API
2. **Get Claims (`GetClaimsAsync`)**: Adjust the claims endpoint and response parsing
3. **Check Warranty (`CheckWarrantyAsync`)**: Update warranty endpoint and response model
4. **Create Claim (`CreateClaimAsync`)**: Ensure multipart form data matches API requirements

### Step 3: Add API Files/Documentation

If you have API specification files (OpenAPI/Swagger, Postman collections, etc.), place them in:

```
VendorWarrantyManager/ApiDocs/
├── dell-tech-direct/
│   └── [your API files]
└── lenovo/
    └── [your API files]
```

### Step 4: Configure API Authentication

Different vendors may use different authentication methods:

- **Bearer Token**: Already implemented (default)
- **API Key**: Add to request headers
- **OAuth**: Implement OAuth flow

Example for API Key authentication (in the service constructor):

```csharp
_httpClient.DefaultRequestHeaders.Add("X-API-Key", "your-api-key");
```

## Building and Running

### Using Visual Studio:

1. Open `VendorWarrantyManager.sln` in Visual Studio
2. Restore NuGet packages (should happen automatically)
3. Build the solution (Ctrl+Shift+B)
4. Run the application (F5)

### Using .NET CLI:

```bash
cd VendorWarrantyManager
dotnet restore
dotnet build
dotnet run --project VendorWarrantyManager/VendorWarrantyManager.csproj
```

## Usage Guide

### 1. Login

- Launch the application
- Select your vendor (Dell Tech Direct or Lenovo)
- Enter your username and password
- Click "Login"

### 2. Dashboard

After successful login, you'll see:

- **Claims List**: Shows all claims (default: your claims)
- **Filter by User**: Enter a username to filter claims
- **Warranty Checker**: Button to check warranty status
- **Make Claim**: Button to create a new claim
- **Refresh**: Reload the claims list

### 3. Check Warranty

- Click "Warranty Checker"
- Enter a service tag or serial number
- Click "Check Warranty"
- View warranty details (status, dates, service level)

### 4. Create Claim

- Click "Make Claim"
- Fill in required fields:
  - Service Tag/Serial Number
  - Issue Description
- Optional fields:
  - Part Number
  - Component Serial Number
- **For Dell**: Add 1-8 images (required)
  - Click "Add Images"
  - Select image files (JPG, PNG)
  - Remove unwanted images
- Click "Submit Claim"

## Dell-Specific Requirements

Dell Tech Direct has specific requirements:

1. **Images are mandatory**: Every claim must have at least 1 image
2. **Maximum 8 images**: Cannot exceed 8 images per claim
3. **Supported formats**: JPG, JPEG, PNG

The application enforces these rules and will show validation errors if requirements aren't met.

## Troubleshooting

### Authentication Fails

- Verify your credentials are correct
- Check that the API endpoints are configured correctly
- Ensure you have network connectivity to the vendor API
- Review API documentation for authentication requirements

### Claims Not Loading

- Check that you're authenticated
- Verify the claims endpoint is correct
- Check console output for error messages
- Ensure the API response format matches the `Claim` model

### Image Upload Issues

- Ensure image files are valid (JPG, PNG)
- Check file size limits (if any from the API)
- Verify the API supports multipart/form-data uploads

## API Error Handling

The application logs errors to the console. To view detailed error messages:

1. Run the application from Visual Studio with debugging (F5)
2. Check the Output window for error details
3. Review the Console for API error messages

## Customization

### Adding More Vendors

To add support for additional vendors:

1. Add new vendor to `Models/VendorType.cs`:
   ```csharp
   public enum VendorType
   {
       Dell,
       Lenovo,
       HP  // New vendor
   }
   ```

2. Create new API service implementing `IVendorApiService`
3. Register service in `App.xaml.cs`:
   ```csharp
   services.AddHttpClient<HpApiService>();
   services.AddTransient<HpApiService>();
   ```

4. Update login window to include new vendor in combo box

### Customizing UI Theme

Edit color scheme in `App.xaml`:

```xml
<SolidColorBrush x:Key="PrimaryColor" Color="#0078D4"/>
<SolidColorBrush x:Key="SecondaryColor" Color="#005A9E"/>
<!-- etc. -->
```

## Dependencies

- **Newtonsoft.Json** (13.0.3): JSON serialization
- **Microsoft.Extensions.DependencyInjection** (8.0.0): Dependency injection
- **Microsoft.Extensions.Http** (8.0.0): HttpClient factory

## License

[Add your license information here]

## Support

For API-specific questions, please refer to:
- Dell Tech Direct API Documentation
- Lenovo Support API Documentation

For application issues, please contact [your support contact]
