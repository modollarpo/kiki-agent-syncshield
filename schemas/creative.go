package schemas

type Creative struct {
	CreativeID  string  `json:"creative_id"`
	Prompt      string  `json:"prompt"`
	Variant     string  `json:"variant"`
	UserID      string  `json:"user_id"`
	ImageURL    *string `json:"image_url,omitempty"`
	BrandSafety *string `json:"brand_safety,omitempty"`
	Ratings     []int   `json:"ratings,omitempty"`
}
