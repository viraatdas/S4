/**
 * Custom theme for SuperTokens UI
 */

export const SuperTokensTheme = {
  colors: {
    background: "#ffffff",
    inputBackground: "#fafafa",
    primary: "#6200ea", // Main purple color
    primaryBorder: "#5000d6",
    primaryHover: "#5000d6",
    primaryText: "#ffffff",
    secondaryText: "#424242",
    success: "#4caf50",
    error: "#f44336",
    textTitle: "#212121",
    textLabel: "#616161",
    textInput: "#212121",
    textLink: "#6200ea",
    textPrimary: "#212121",
    textGray: "#757575",
    divider: "#eeeeee",
    buttonText: "#ffffff",
    headerTitle: "#212121",
    socialButtonText: "#212121",
    socialButtonBackground: "#ffffff",
    socialButtonBorder: "#e0e0e0",
  },
  
  fonts: {
    size: {
      tiny: "0.75rem",
      small: "0.875rem",
      base: "1rem",
      medium: "1.25rem",
      large: "1.5rem",
    },
    weight: {
      light: 300,
      normal: 400,
      medium: 500,
      bold: 600,
    },
    family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
  },
  
  borders: {
    radius: "8px",
    width: "1px",
    style: "solid",
  },
  
  shadows: {
    small: "0 2px 4px rgba(0, 0, 0, 0.05)",
    medium: "0 4px 8px rgba(0, 0, 0, 0.1)",
    large: "0 8px 16px rgba(0, 0, 0, 0.15)",
  },
  
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
  },
  
  // Custom styles for specific components
  components: {
    container: {
      maxWidth: "450px",
      width: "100%",
      margin: "0 auto",
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
      borderRadius: "12px",
      padding: "2rem",
      boxSizing: "border-box",
    },
    
    divider: {
      margin: "1.5rem 0",
    },
    
    button: {
      height: "44px",
      fontWeight: 500,
      textTransform: "none",
      borderRadius: "8px",
      padding: "0 1.5rem",
    },
    
    input: {
      height: "44px",
      borderRadius: "8px",
      padding: "0 1rem",
    },
    
    headerTitle: {
      fontSize: "1.5rem",
      fontWeight: 600,
      marginBottom: "1.5rem",
    },
    
    socialButton: {
      height: "44px",
      borderRadius: "8px",
      fontWeight: 500,
      boxShadow: "0 2px 4px rgba(0, 0, 0, 0.05)",
    },
  },
};
