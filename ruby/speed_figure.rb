# frozen_string_literal: true

require "csv"

module HorseRacingPredictor
  module SpeedFigure
    SOURCE_WEIGHTS = {
      "csv" => 0.9,
      "drf" => 1.0,
      "dr2" => 1.05,
      "dr3" => 1.1,
      "dr4" => 1.15,
      "drf2" => 1.05,
      "drf3" => 1.1,
      "drf4" => 1.15
    }.freeze

    METRIC_WEIGHTS = {
      "speed" => 0.45,
      "pace" => 0.25,
      "class" => 0.2,
      "weight" => -0.1
    }.freeze

    module_function

    def mean(values)
      return 0.0 if values.empty?

      values.sum / values.length.to_f
    end

    def stddev(values)
      return 0.0 if values.empty?

      mu = mean(values)
      variance = values.sum { |v| (v - mu)**2 } / values.length.to_f
      Math.sqrt(variance)
    end

    def zscores(values)
      mu = mean(values)
      sigma = stddev(values)
      return Array.new(values.length, 0.0) if sigma.zero?

      values.map { |v| (v - mu) / sigma }
    end

    def compute(rows, source_type)
      numeric = %w[speed pace class weight]
      series = numeric.to_h { |k| [k, rows.map { |r| r[k].to_f }] }
      z = series.transform_values { |vals| zscores(vals) }

      multiplier = SOURCE_WEIGHTS.fetch(source_type.downcase, 1.0)

      rows.each_with_index.map do |row, idx|
        composite = METRIC_WEIGHTS.sum { |metric, weight| z[metric][idx] * weight }
        base = 100 + (composite * 12)
        row.merge("proprietary_speed_figure" => (base * multiplier).round(2))
      end
    end
  end
end
