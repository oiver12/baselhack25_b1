"use client";

interface NobleMessage {
  cluster: string;
  message_content: string;
  username: string;
  bulletpoint: string[];
  profile_pic_url: string;
  cluster_label: string;
}

interface ClusterExpertsProps {
  nobleMessages: Record<string, NobleMessage>;
}

export default function ClusterExperts({ nobleMessages }: ClusterExpertsProps) {
  const experts = Object.values(nobleMessages);

  if (experts.length === 0) {
    return null;
  }

  // Color palette for clusters
  const clusterColors = [
    { bg: "rgba(59, 130, 246, 0.1)", border: "#3b82f6", accent: "#2563eb" }, // Blue
    { bg: "rgba(168, 85, 247, 0.1)", border: "#a855f7", accent: "#9333ea" }, // Purple
    { bg: "rgba(34, 197, 94, 0.1)", border: "#22c55e", accent: "#16a34a" }, // Green
    { bg: "rgba(245, 158, 11, 0.1)", border: "#f59e0b", accent: "#d97706" }, // Amber
  ];

  return (
    <div className="space-y-6">
      <h2
        className="text-2xl font-bold mb-6 text-black print:text-black"
        style={{ color: "#000000" }}
      >
        Cluster Experts
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 print:grid-cols-2">
        {experts.map((expert, index) => {
          const colors = clusterColors[index % clusterColors.length];

          return (
            <div
              key={expert.cluster_label}
              className="relative rounded-2xl shadow-2xl border backdrop-blur-xl p-6 transition-all duration-300 hover:scale-[1.02] hover:shadow-3xl print:shadow-none print:border-2 print:border-gray-300 print:backdrop-blur-none print:hover:scale-100"
              style={{
                backgroundColor: "white",
                borderColor: colors.border,
                borderWidth: "2px",
                boxShadow: `0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2), 0 0 0 1px ${colors.border}40`,
              }}
            >
              {/* Decorative corner accent */}
              <div
                className="absolute top-0 right-0 w-24 h-24 rounded-bl-full -z-10 opacity-20"
                style={{
                  backgroundColor: colors.border,
                }}
              />

              {/* Blurred background overlay */}
              <div
                className="absolute inset-0 rounded-2xl -z-10 backdrop-blur-2xl print:hidden"
                style={{
                  backgroundColor: colors.bg,
                  opacity: 0.5,
                }}
              />

              <div className="relative space-y-4">
                {/* Expert Header */}
                <div className="flex flex-col items-center space-y-3">
                  {/* Profile Picture */}
                  <div
                    className="relative w-20 h-20 rounded-full overflow-hidden ring-4 transition-all duration-300 hover:ring-6"
                    style={{
                      ringColor: colors.border,
                      boxShadow: `0 8px 16px ${colors.border}40`,
                    }}
                  >
                    {expert.profile_pic_url ? (
                      <img
                        src={expert.profile_pic_url}
                        alt={expert.username}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          // Fallback to initials if image fails to load
                          const target = e.target as HTMLImageElement;
                          target.style.display = "none";
                          const parent = target.parentElement;
                          if (parent) {
                            const fallback = document.createElement("div");
                            fallback.className =
                              "w-full h-full flex items-center justify-center text-2xl font-bold text-white";
                            fallback.style.backgroundColor = colors.border;
                            fallback.textContent = expert.username
                              .charAt(0)
                              .toUpperCase();
                            parent.appendChild(fallback);
                          }
                        }}
                      />
                    ) : (
                      <div
                        className="w-full h-full flex items-center justify-center text-2xl font-bold text-white"
                        style={{
                          backgroundColor: colors.border,
                        }}
                      >
                        {expert.username.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>

                  {/* Name and Cluster Label */}
                  <div className="text-center">
                    <h3
                      className="font-bold text-lg mb-1"
                      style={{ color: colors.accent }}
                    >
                      {expert.username}
                    </h3>
                    <div
                      className="inline-block px-3 py-1 rounded-full text-xs font-semibold"
                      style={{
                        backgroundColor: colors.bg,
                        color: colors.accent,
                        border: `1px solid ${colors.border}`,
                      }}
                    >
                      {expert.cluster_label}
                    </div>
                  </div>
                </div>

                {/* Expertise Bullet Points */}
                <div className="space-y-2">
                  <h4
                    className="text-xs font-semibold uppercase tracking-wide mb-3"
                    style={{ color: "#6b7280" }}
                  >
                    Areas of Expertise
                  </h4>
                  <ul className="space-y-2">
                    {expert.bulletpoint.map((bullet, bulletIndex) => (
                      <li
                        key={bulletIndex}
                        className="flex items-start gap-2 text-sm"
                        style={{ color: "#374151" }}
                      >
                        <span
                          className="flex-shrink-0 mt-1.5 w-1.5 h-1.5 rounded-full"
                          style={{
                            backgroundColor: colors.border,
                          }}
                        />
                        <span className="flex-1 leading-relaxed">{bullet}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Divider */}
                <div
                  className="h-px my-4"
                  style={{
                    background: `linear-gradient(90deg, transparent, ${colors.border}60, transparent)`,
                  }}
                />

                {/* Noble Message */}
                <div className="space-y-2">
                  <h4
                    className="text-xs font-semibold uppercase tracking-wide"
                    style={{ color: "#6b7280" }}
                  >
                    Representative Message
                  </h4>
                  <p
                    className="text-xs leading-relaxed italic"
                    style={{
                      color: "#6b7280",
                      lineHeight: "1.6",
                    }}
                  >
                    &ldquo;{expert.message_content}&rdquo;
                  </p>
                </div>
              </div>

              {/* Glow effect on hover */}
              <div
                className="absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 pointer-events-none hover:opacity-100 print:hidden"
                style={{
                  boxShadow: `0 0 30px ${colors.border}30`,
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
