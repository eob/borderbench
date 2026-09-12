export type BorderSides = "all-4" | "bottom-only" | "left-only" | "top-only" | "none";
export type StrokeStyle = "solid" | "dashed" | "dotted" | "none";
export type StrokeWidth = "0px" | "1px" | "2px" | "4px" | "8px";
export type CornerRadius = "sharp" | "subtle" | "medium" | "large" | "pill";
export type CornerUniformity = "all-corners" | "top-only" | "asymmetric";
export type Elevation = "none" | "subtle-drop" | "floating-drop";
export type BackgroundTheme = 
  | "white-on-gray"
  | "white-on-white"
  | "gray-tint-on-white"
  | "blue-tint-on-white"
  | "dark-mode";

export interface MatchedBlock { id: string; axis: string; level: string; }
export interface DesignEvidence { recipeId: string; matchedBlocks: MatchedBlock[]; }

export interface BorderSpecimenConfig {
  design?: DesignEvidence;
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

export interface RenderedEvidence {
  browser: string;
  platform: string;
  viewport: { width: number; height: number; deviceScaleFactor: number };
  card: { x: number; y: number; width: number; height: number };
  computed: Record<string, string>;
  font: { path: string; sha256: string; family: string; platformFonts: { familyName: string; isCustomFont: boolean; glyphCount: number }[] };
  reference: { fontFamily: string; fontSizePx: number; lineHeightPx: number; ruleWidthPx: number };
  shadowReference?: { imageFilename: string; imageSha256: string };
}

export interface BorderBenchmarkManifestItem {
  taskId: string;
  design?: DesignEvidence;
  imagePath: string;
  imageFilename: string;
  imageSha256?: string;
  rendered?: RenderedEvidence;
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
