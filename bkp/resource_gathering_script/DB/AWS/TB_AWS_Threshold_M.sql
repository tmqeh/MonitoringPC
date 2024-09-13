USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_AWS_Threshold_M]    Script Date: 2022-02-11 ¿ÀÀü 9:34:25 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_AWS_Threshold_M](
	[SVC_NM] [varchar](100) NOT NULL,
	[Rsrc_Name] [varchar](100) NOT NULL,
	[THRHL_VAL] [int] NOT NULL,
	[VPC] [varchar](30) NULL,
	[Use_YN] [varchar](1) NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_AWS_Threshold_M] PRIMARY KEY CLUSTERED 
(
	[SVC_NM] ASC,
	[Rsrc_Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[TB_AWS_Threshold_M] ADD  DEFAULT ('Y') FOR [Use_YN]
GO


