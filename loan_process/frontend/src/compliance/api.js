// Import the shared API utility
import { createApiInstance } from '../utils/apiUtils';

// Create a compliance-specific API instance with the shared utility
// This allows for compliance-specific customization if needed in the future
const complianceAPI = createApiInstance();

export default complianceAPI;
