// api.js
// Import the shared API utility
import { createApiInstance } from '../utils/apiUtils';

// Create a user-specific API instance with the shared utility
// This allows for user-specific customization if needed in the future
const userAPI = createApiInstance();

export default userAPI;
