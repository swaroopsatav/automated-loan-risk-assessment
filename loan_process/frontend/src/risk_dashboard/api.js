// Import the shared API utility
import { createApiInstance } from '../utils/apiUtils';

// Create a risk-specific API instance with the shared utility
// This allows for risk-specific customization if needed in the future
const riskAPI = createApiInstance();

export default riskAPI;
