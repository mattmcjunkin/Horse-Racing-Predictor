#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "csv"
require_relative "../ruby/speed_figure"

if ARGV.empty?
  warn "Usage: ruby scripts/analyze_card.rb path/to/card.csv [source_type]"
  exit 1
end

path = ARGV[0]
source_type = (ARGV[1] || File.extname(path).delete_prefix(".")).downcase

rows = CSV.read(path, headers: true).map do |row|
  {
    "horse" => row["horse"] || row["horse_name"] || row["runner"] || row[0],
    "speed" => row["speed"] || row["speed_rating"] || 0,
    "pace" => row["pace"] || row["pace_rating"] || 0,
    "class" => row["class"] || row["class_rating"] || 0,
    "weight" => row["weight"] || row["carried_weight"] || 0
  }
end

scored = HorseRacingPredictor::SpeedFigure.compute(rows, source_type)
puts JSON.pretty_generate(scored)
