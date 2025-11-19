using System.Collections.Generic;
using System.Threading.Tasks;
using VendorWarrantyManager.Models;

namespace VendorWarrantyManager.Services
{
    public interface IVendorApiService
    {
        Task<bool> AuthenticateAsync(string username, string password);
        Task<List<Claim>> GetClaimsAsync(string? filterByUser = null);
        Task<WarrantyInfo> CheckWarrantyAsync(string serviceTag);
        Task<Claim> CreateClaimAsync(CreateClaimRequest request);
        VendorType GetVendorType();
    }
}
