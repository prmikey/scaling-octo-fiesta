using System;
using System.Collections.Generic;

namespace VendorWarrantyManager.Models
{
    public class Claim
    {
        public string ClaimId { get; set; } = string.Empty;
        public string ServiceTag { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public DateTime CreatedDate { get; set; }
        public string Status { get; set; } = string.Empty;
        public string CreatedBy { get; set; } = string.Empty;
        public VendorType Vendor { get; set; }
        public List<string>? ImagePaths { get; set; }
        public string? PartNumber { get; set; }
        public string? SerialNumber { get; set; }
    }
}
