namespace VendorWarrantyManager.Models
{
    public class UserCredentials
    {
        public VendorType Vendor { get; set; }
        public string Username { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
        public string? Token { get; set; }
    }
}
