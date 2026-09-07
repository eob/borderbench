export type BorderSides = "all-4" | "bottom-only" | "left-only" | "top-only" | "none";
export type StrokeStyle = "solid" | "dashed" | "dotted" | "double" | "none";
export type StrokeWidth = "0px" | "1px" | "2px" | "4px" | "8px";
export type CornerRadius = "sharp" | "subtle" | "medium" | "large" | "pill";
export type CornerUniformity = "all-corners" | "top-only" | "asymmetric";
export type Elevation = "none" | "subtle-drop" | "floating-drop" | "ring-only" | "stroke+shadow";
export type BackgroundTheme = 
  | "white-on-gray"
  | "white-on-white"
  | "gray-tint-on-white"
  | "blue-tint-on-white"
  | "dark-mode";

export interface BorderSpecimenConfig {
  id: string;
  has_border: boolean;
  border_sides: BorderSides;
  stroke_style: StrokeStyle;
  stroke_width: StrokeWidth;
  stroke_width_px: number;
  corner_radius: CornerRadius;
  corner_radius_px: number | [number, number, number, number];
  corner_uniformity: CornerUniformity;
  elevation: Elevation;
  theme: BackgroundTheme;
  title: string;
  subtitle: string;
  tag: string;
}

export interface BorderBenchmarkManifestItem {
  taskId: string;
  imagePath: string;
  imageFilename: string;
  groundTruth: {
    has_border: boolean;
    border_sides: BorderSides;
    stroke_style: StrokeStyle;
    stroke_width: StrokeWidth;
    stroke_width_px: number;
    corner_radius: CornerRadius;
    corner_radius_px: number | [number, number, number, number];
    corner_uniformity: CornerUniformity;
    elevation: Elevation;
    theme: BackgroundTheme;
  };
  prompt: string;
}
