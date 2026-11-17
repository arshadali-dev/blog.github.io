# frozen_string_literal: true

Jekyll::Hooks.register :documents, :pre_render do |document|
  document.data["image"] ||= document.data["feature-img"]
end
