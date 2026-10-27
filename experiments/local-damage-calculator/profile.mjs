// Research-only D&D 2024 numeric profile. Not a platform Core or approved rule package.
export const PROFILE_ID = 'research.dnd2024-srd521';
export const PROFILE_REVISION = 'draft-1';
export const DAMAGE_LIMIT = 1_000_000;
export const DAMAGE_TYPES = Object.freeze(['acid', 'bludgeoning', 'cold', 'fire', 'force',
  'lightning', 'necrotic', 'piercing', 'poison', 'psychic', 'radiant', 'slashing', 'thunder']);
export const RULES = Object.freeze({
  ability: 'SRD5.2.1:p16; selected synthetic ability definition',
  resistance: 'SRD5.2.1:p17:Resistance; p187:Round Down',
  vulnerability: 'SRD5.2.1:p17:Vulnerability and Order of Application',
  immunity: 'SRD5.2.1:p17:Immunity',
});
