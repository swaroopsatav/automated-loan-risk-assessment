// Import the shared API utility
import { createApiInstance } from '../utils/apiUtils';

// Create an integrations-specific API instance with the shared utility
// This allows for integrations-specific customization if needed in the future
const integrationsAPI = createApiInstance();

export default integrationsAPI;
