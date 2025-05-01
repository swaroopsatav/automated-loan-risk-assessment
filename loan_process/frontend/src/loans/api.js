// Import the shared API utility
import { createApiInstance } from '../utils/apiUtils';

// Create a loan-specific API instance with the shared utility
// This allows for loan-specific customization if needed in the future
const loanAPI = createApiInstance();

export default loanAPI;
