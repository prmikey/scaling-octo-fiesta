using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using VendorWarrantyManager.Models;

namespace VendorWarrantyManager.Services
{
    public class LenovoApiService : IVendorApiService
    {
        private readonly HttpClient _httpClient;
        private string? _authToken;
        private string? _currentUser;

        // TODO: Replace with actual Lenovo API endpoints
        private const string BASE_URL = "https://support.lenovo.com/api";
        private const string AUTH_ENDPOINT = "/auth/login";
        private const string CLAIMS_ENDPOINT = "/claims";
        private const string WARRANTY_ENDPOINT = "/warranty";

        public LenovoApiService(HttpClient httpClient)
        {
            _httpClient = httpClient;
            _httpClient.BaseAddress = new Uri(BASE_URL);
        }

        public async Task<bool> AuthenticateAsync(string username, string password)
        {
            try
            {
                var loginRequest = new
                {
                    username = username,
                    password = password
                };

                var json = JsonConvert.SerializeObject(loginRequest);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync(AUTH_ENDPOINT, content);

                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var authResponse = JsonConvert.DeserializeObject<dynamic>(responseContent);

                    _authToken = authResponse?.token;
                    _currentUser = username;

                    // Set default authorization header
                    _httpClient.DefaultRequestHeaders.Authorization =
                        new AuthenticationHeaderValue("Bearer", _authToken);

                    return true;
                }

                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Lenovo Auth Error: {ex.Message}");
                return false;
            }
        }

        public async Task<List<Claim>> GetClaimsAsync(string? filterByUser = null)
        {
            try
            {
                var user = filterByUser ?? _currentUser;
                var endpoint = $"{CLAIMS_ENDPOINT}?user={user}";

                var response = await _httpClient.GetAsync(endpoint);

                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    var claims = JsonConvert.DeserializeObject<List<Claim>>(content);

                    // Set vendor type for all claims
                    claims?.ForEach(c => c.Vendor = VendorType.Lenovo);

                    return claims ?? new List<Claim>();
                }

                return new List<Claim>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Lenovo Get Claims Error: {ex.Message}");
                return new List<Claim>();
            }
        }

        public async Task<WarrantyInfo> CheckWarrantyAsync(string serviceTag)
        {
            try
            {
                var endpoint = $"{WARRANTY_ENDPOINT}/{serviceTag}";
                var response = await _httpClient.GetAsync(endpoint);

                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    var warranty = JsonConvert.DeserializeObject<WarrantyInfo>(content);

                    return warranty ?? new WarrantyInfo { ServiceTag = serviceTag, IsValid = false };
                }

                return new WarrantyInfo { ServiceTag = serviceTag, IsValid = false };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Lenovo Warranty Check Error: {ex.Message}");
                return new WarrantyInfo { ServiceTag = serviceTag, IsValid = false };
            }
        }

        public async Task<Claim> CreateClaimAsync(CreateClaimRequest request)
        {
            try
            {
                // Lenovo may have different requirements - images are optional
                var formContent = new MultipartFormDataContent();
                formContent.Add(new StringContent(request.ServiceTag), "serviceTag");
                formContent.Add(new StringContent(request.Description), "description");

                if (!string.IsNullOrEmpty(request.PartNumber))
                    formContent.Add(new StringContent(request.PartNumber), "partNumber");

                if (!string.IsNullOrEmpty(request.SerialNumber))
                    formContent.Add(new StringContent(request.SerialNumber), "serialNumber");

                if (!string.IsNullOrEmpty(request.IssueCategory))
                    formContent.Add(new StringContent(request.IssueCategory), "issueCategory");

                // Add images if provided
                if (request.Images != null)
                {
                    for (int i = 0; i < request.Images.Count; i++)
                    {
                        var imageContent = new ByteArrayContent(request.Images[i]);
                        imageContent.Headers.ContentType = MediaTypeHeaderValue.Parse("image/jpeg");
                        formContent.Add(imageContent, $"image{i + 1}", $"image{i + 1}.jpg");
                    }
                }

                var response = await _httpClient.PostAsync(CLAIMS_ENDPOINT, formContent);

                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    var claim = JsonConvert.DeserializeObject<Claim>(content);

                    if (claim != null)
                    {
                        claim.Vendor = VendorType.Lenovo;
                        return claim;
                    }
                }

                throw new Exception("Failed to create Lenovo claim");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Lenovo Create Claim Error: {ex.Message}");
                throw;
            }
        }

        public VendorType GetVendorType()
        {
            return VendorType.Lenovo;
        }
    }
}
