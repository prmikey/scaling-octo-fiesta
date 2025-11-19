using System.Collections.Generic;

namespace VendorWarrantyManager.Models
{
    public class CreateClaimRequest
    {
        public string ServiceTag { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string? PartNumber { get; set; }
        public string? SerialNumber { get; set; }
        public List<byte[]>? Images { get; set; } // For Dell - max 8 images
        public string? IssueCategory { get; set; }
    }
}
