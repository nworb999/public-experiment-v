/**
 * Logger Module
 * Provides logging functionality for debugging
 */

const Logger = {
    log(message, data) {
        console.log(`[DEBUG] ${message}`, data);
    }
};

export default Logger; 