-- 为世界观表添加更多字段
ALTER TABLE worldviews ADD COLUMN name VARCHAR(200);
ALTER TABLE worldviews ADD COLUMN element_type VARCHAR(100);
ALTER TABLE worldviews ADD COLUMN power_level VARCHAR(100);
ALTER TABLE worldviews ADD COLUMN scope VARCHAR(100);
ALTER TABLE worldviews ADD COLUMN rules TEXT;
ALTER TABLE worldviews ADD COLUMN conflicts TEXT;
ALTER TABLE worldviews ADD COLUMN evolution TEXT;
ALTER TABLE worldviews ADD COLUMN related_characters TEXT;
ALTER TABLE worldviews ADD COLUMN related_locations TEXT;
ALTER TABLE worldviews ADD COLUMN related_items TEXT;
ALTER TABLE worldviews ADD COLUMN examples TEXT;
ALTER TABLE worldviews ADD COLUMN references TEXT;
ALTER TABLE worldviews ADD COLUMN first_mentioned_chapter INTEGER;
ALTER TABLE worldviews ADD COLUMN appearance_chapters TEXT;

-- 为地点表添加更多字段
ALTER TABLE locations ADD COLUMN culture TEXT;
ALTER TABLE locations ADD COLUMN population VARCHAR(100);
ALTER TABLE locations ADD COLUMN government VARCHAR(200);
ALTER TABLE locations ADD COLUMN economy TEXT;
ALTER TABLE locations ADD COLUMN history TEXT;
ALTER TABLE locations ADD COLUMN related_events TEXT;
ALTER TABLE locations ADD COLUMN native_species TEXT;
ALTER TABLE locations ADD COLUMN resources TEXT;

-- 为物品表添加更多字段  
ALTER TABLE items ADD COLUMN crafting_method TEXT;
ALTER TABLE items ADD COLUMN materials TEXT;
ALTER TABLE items ADD COLUMN effects TEXT;
ALTER TABLE items ADD COLUMN side_effects TEXT;
ALTER TABLE items ADD COLUMN usage_conditions TEXT;
ALTER TABLE items ADD COLUMN durability VARCHAR(100);
ALTER TABLE items ADD COLUMN value VARCHAR(100);
ALTER TABLE items ADD COLUMN related_events TEXT;
