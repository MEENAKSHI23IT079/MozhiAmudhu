from transformers import NllbTokenizerFast
tok = NllbTokenizerFast.from_pretrained("nllb-fixed")

print("Has lang_code_to_id =", hasattr(tok, "lang_code_to_id"))
print("Tamil id =", tok.lang_code_to_id.get("tam_Taml"))
