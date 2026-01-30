// Design tokens for KIKI Agent™ UI
export const colors = {
  primary: {
    100: '#E6F0FF',
    200: '#B3D1FF',
    300: '#80B3FF',
    400: '#3385FF',
    500: '#0057D9',
    600: '#003C99',
  },
  secondary: {
    100: '#F0F6FF',
    200: '#D1E0FF',
    300: '#A3C2FF',
    400: '#6699FF',
    500: '#3366FF',
    600: '#254EDB',
  },
  neutral: {
    100: '#F8F9FA',
    200: '#E9ECEF',
    300: '#DEE2E6',
    400: '#ADB5BD',
    500: '#495057',
    600: '#212529',
  },
  success: '#27AE60',
  warning: '#F2C94C',
  error: '#EB5757',
  info: '#2D9CDB',
};

export const typography = {
  fontFamily: 'Inter, Arial, sans-serif',
  headings: {
    fontWeight: 700,
    lineHeight: 1.2,
  },
  body: {
    fontWeight: 400,
    lineHeight: 1.5,
  },
  data: {
    fontWeight: 500,
    lineHeight: 1.3,
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 40,
};

export const radii = {
  sm: 4,
  md: 8,
  lg: 16,
};

export const shadows: { [key: string]: string } = {
  sm: '0 1px 2px rgba(0,0,0,0.04)',
  md: '0 4px 12px rgba(0,0,0,0.08)',
  lg: '0 8px 24px rgba(0,0,0,0.12)',
};
