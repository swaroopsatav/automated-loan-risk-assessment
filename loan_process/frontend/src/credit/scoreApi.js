// Import the shared API utility
import { createApiInstance } from '../utils/apiUtils';

// Create a score-specific API instance with the shared utility
// This allows for score-specific customization if needed in the future
const scoreApi = createApiInstance();

export default scoreApi;
