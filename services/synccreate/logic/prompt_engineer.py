
class PromptEngineer:
    def __init__(self):
        self.brand_voice = "High-end, minimalist, professional, luxury lighting"
        self.negative_prompts = "blurry, low quality, distorted hands, text, watermark"

    def craft_prompt(self, audience_segment: str, ltv_score: float, product_desc: str):
        """
        Dynamically engineers a prompt based on KIKI's internal intelligence.
        """
        # Step 1: Adjust 'Vibe' based on LTV
        aesthetic = "cinematic, 8k, editorial photography" if ltv_score > 0.8 else "vibrant, engaging, social-media style"
        # Step 2: Inject Audience-specific modifiers
        audience_hooks = {
            "luxury": "rich textures, gold accents, soft bokeh",
            "tech": "neon highlights, clean lines, futuristic",
            "lifestyle": "natural sunlight, candid, warm tones"
        }
        hook = audience_hooks.get(audience_segment.lower(), "professional studio lighting")
        # Step 3: Final Composition
        final_prompt = f"{product_desc}, {hook}, {aesthetic}, {self.brand_voice} --no {self.negative_prompts}"
        return final_prompt

class MultimediaPromptEngineer(PromptEngineer):
    def craft_video_prompt(self, audience_segment: str, product_desc: str):
        """
        Engineers a prompt specifically for video generation models.
        """
        # Define cinematic motion based on audience
        motion_style = {
            "luxury": "slow-motion tracking shot, elegant camera slide, shallow depth of field",
            "tech": "fast-paced hyper-lapse, glitch transitions, dynamic lighting shifts",
            "lifestyle": "handheld natural movement, golden hour light transition"
        }
        style = motion_style.get(audience_segment.lower(), "steady pan")
        base_prompt = self.craft_prompt(audience_segment, 0.9, product_desc) # Use static logic for base
        # Add temporal descriptors
        return f"{base_prompt}. {style}, high-fidelity 4k, cinematic textures, 24fps."

    def craft_prompt(self, audience_segment: str, ltv_score: float, product_desc: str):
        """
        Dynamically engineers a prompt based on KIKI's internal intelligence.
        """
        # Step 1: Adjust 'Vibe' based on LTV
        aesthetic = "cinematic, 8k, editorial photography" if ltv_score > 0.8 else "vibrant, engaging, social-media style"
        
        # Step 2: Inject Audience-specific modifiers
        audience_hooks = {
            "luxury": "rich textures, gold accents, soft bokeh",
            "tech": "neon highlights, clean lines, futuristic",
            "lifestyle": "natural sunlight, candid, warm tones"
        }
        
        hook = audience_hooks.get(audience_segment.lower(), "professional studio lighting")
        
        # Step 3: Final Composition
        final_prompt = f"{product_desc}, {hook}, {aesthetic}, {self.brand_voice} --no {self.negative_prompts}"
        return final_prompt
